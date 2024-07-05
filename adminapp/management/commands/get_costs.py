import json
from datetime import datetime, timedelta
from pprint import pprint

import pytz
import requests
from django.core.management import BaseCommand

import config
from adminapp.models import Account, Cost, Cabinet, Campaign, Ad, AdSet, Action, Update


def get_data(fbtool_id, date):
    params = {
        "key": config.FBTOOL_KEY,
        "account": fbtool_id,
        "dates": f"{date} - {date}",
        "mode": "ads",
        "status": "all",
        "byDay": 1
    }
    response = requests.get('https://fbtool.pro/api/get-statistics/', params=params)
    return response.json()


def process_data(cabinet_data, date, currencies, definitive=False):
    updated_campaigns = {}
    updated_adsets = {}
    cabinet_id = int(cabinet_data['account_id'])
    cabinet = Cabinet.objects.get(pk=cabinet_id)
    for ad_data in cabinet_data['ads']['data']:

        campaign_id = int(ad_data['campaign']['id'])
        if campaign_id not in updated_campaigns.keys():
            campaign_check = Campaign.objects.filter(pk=campaign_id)
            campaign_data = ad_data['campaign']
            if campaign_check.exists():
                campaign = campaign_check.first()
                campaign.name = campaign_data['name']
                campaign.status = campaign_data['status']
                campaign.effective_status = campaign_data['effective_status']
                campaign.save()
                updated_campaigns[campaign_id] = campaign
            else:
                campaign_data['cabinet'] = cabinet
                campaign = Campaign.objects.create(**campaign_data)
        else:
            campaign = updated_campaigns[campaign_id]

        adset_id = int(ad_data['adset']['id'])
        if adset_id not in updated_adsets.keys():
            adset_check = AdSet.objects.filter(pk=adset_id)
            adset_data = ad_data['adset']
            if adset_check.exists():
                adset = adset_check.first()
                adset.name = adset_data['name']
                adset.status = adset_data['status']
                adset.effective_status = adset_data['effective_status']
                adset.save()
                updated_adsets[adset_id] = adset
            else:
                adset_data['campaign'] = campaign
                adset = AdSet.objects.create(**adset_data)
        else:
            adset = updated_adsets[adset_id]

        ad_id = int(ad_data['id'])
        ad_check = Ad.objects.filter(pk=ad_id)

        insights = None
        if 'insights' in ad_data.keys():
            insights = ad_data['insights']['data']
            del ad_data['insights']
        if ad_check.exists():
            ad = ad_check.first()
            ad.name = ad_data['name']
            ad.status = ad_data['status']
            ad.effective_status = ad_data['effective_status']
            ad.creative = ad_data['creative']
            ad.save()
        else:
            ad_data['adset'] = adset
            del ad_data['campaign']
            ad = Ad.objects.create(**ad_data)

        if insights is not None:
            Cost.objects.filter(ad__pk=ad.pk, date=date).delete()

            for insight in insights:
                actions = []
                cpat = []

                if 'actions' in insight.keys():
                    actions = insight['actions']
                    del insight['actions']
                if 'cost_per_action_type' in insight.keys():
                    cpat = insight['cost_per_action_type']
                    del insight['cost_per_action_type']

                insight['ad'] = ad
                insight['date'] = date
                insight['definitive'] = definitive
                insight['amount'] = insight['spend']
                insight['amount_USD'] = round(float(insight['amount']) * currencies[cabinet.currency.lower()]['inverseRate'], 2) if cabinet.currency != 'USD' else insight['amount']
                del insight['spend']
                del insight['date_start']
                del insight['date_stop']
                cost = Cost.objects.create(**insight)

                actions_to_create = {a['action_type']: {'count': a['value'], 'type': a['action_type'], 'cost': cost}
                                     for a in actions}
                for action in cpat:
                    actions_to_create[action['action_type']]['value'] = action['value']

                for action in actions_to_create.values():
                    Action.objects.create(**action)


class Command(BaseCommand):

    def handle(self, *args, **options):
        currencies = requests.get('https://www.floatrates.com/daily/usd.json').json()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        accounts = Account.objects.all()
        for account in accounts:
            today_data = get_data(account.fbtool_id, today)
            yesterday_data = get_data(account.fbtool_id, yesterday)
            tomorrow_data = get_data(account.fbtool_id, tomorrow)

            today_data = {a['account_id']: a for a in today_data['data']}
            yesterday_data = {a['account_id']: a for a in yesterday_data['data']}
            tomorrow_data = {a['account_id']: a for a in tomorrow_data['data']}

            cab_params = {
                "key": config.FBTOOL_KEY,
                "account": account.fbtool_id
            }
            cab_response = requests.get('https://fbtool.pro/api/get-adaccounts/', params=cab_params)
            cab_response_json = cab_response.json()
            for cab in cab_response_json['data']:
                cabinet_check = Cabinet.objects.filter(pk=cab['account_id'])
                cab['fbtool_id'] = cab['id']
                cab['id'] = cab['account_id']
                del cab['account_id']
                cab['timezone'] = cab['timezone_name']
                del cab['timezone_name']
                cab['status'] = cab['account_status']
                del cab['account_status']
                if cabinet_check.exists():
                    cabinet = cabinet_check.first()
                    for param, value in cab.items():
                        setattr(cabinet, param, value)
                    cabinet.save()
                else:
                    cab['account'] = account
                    Cabinet.objects.create(**cab)

            for cabinet in account.get_cabinets:
                date = datetime.now(pytz.timezone(cabinet.timezone)).date()
                str_cabinet_pk = str(cabinet.pk)
                if ((date == yesterday or (date == today
                                           and Cost.objects.filter(date=yesterday, definitive=False,
                                                                   ad__adset__campaign__cabinet__pk=cabinet.pk).exists()))
                        and str_cabinet_pk in yesterday_data.keys() and 'ads' in yesterday_data[str_cabinet_pk].keys()):
                    process_data(yesterday_data[str_cabinet_pk], yesterday, currencies, date == today)

                if ((date == today or (date == tomorrow
                                       and Cost.objects.filter(date=today, definitive=False,
                                                               ad__adset__campaign__cabinet__pk=cabinet.pk).exists()))
                        and str_cabinet_pk in today_data.keys() and 'ads' in today_data[str_cabinet_pk].keys()):
                    process_data(today_data[str_cabinet_pk], today, currencies, date == tomorrow)

                if (date == tomorrow and str_cabinet_pk in tomorrow_data.keys()
                        and 'ads' in tomorrow_data[str_cabinet_pk].keys()):
                    process_data(tomorrow_data[str_cabinet_pk], tomorrow, currencies)

        Update.objects.create(type='costs', datetime=datetime.now())
