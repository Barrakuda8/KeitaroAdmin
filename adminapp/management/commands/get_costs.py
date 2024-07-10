from datetime import datetime, timedelta
from pprint import pprint

import pytz
import requests
from django.core.management import BaseCommand

import config
from adminapp.models import Account, Cost, Cabinet, Update


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


class Command(BaseCommand):

    def handle(self, *args, **options):
        update = Update.objects.create(type='costs', datetime=datetime.now(), finished=False)
        currencies = requests.get('https://www.floatrates.com/daily/usd.json').json()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        accounts = Account.objects.all()
        for account in accounts:
            today_data = get_data(account.fbtool_id, today)
            yesterday_data = get_data(account.fbtool_id, yesterday)
            tomorrow_data = get_data(account.fbtool_id, tomorrow)

            if 'data' in today_data.keys() and 'data' in yesterday_data.keys() \
               and 'data' in tomorrow_data.keys():
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
                        cabinet.update_costs(cabinet_data=yesterday_data[str_cabinet_pk], currencies=currencies)

                    if ((date == today or (date == tomorrow
                                           and Cost.objects.filter(date=today, definitive=False,
                                                                   ad__adset__campaign__cabinet__pk=cabinet.pk).exists()))
                            and str_cabinet_pk in today_data.keys() and 'ads' in today_data[str_cabinet_pk].keys()):
                        cabinet.update_costs(cabinet_data=today_data[str_cabinet_pk], currencies=currencies)

                    if (date == tomorrow and str_cabinet_pk in tomorrow_data.keys()
                            and 'ads' in tomorrow_data[str_cabinet_pk].keys()):
                        cabinet.update_costs(cabinet_data=tomorrow_data[str_cabinet_pk], currencies=currencies)

        update.finished = True
        update.save()

