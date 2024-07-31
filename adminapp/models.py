import random
import string
from datetime import datetime, timedelta
from pprint import pprint

import pytz
import requests
from django.db import models
from django.dispatch import receiver

import config
from authapp.models import User


class Update(models.Model):

    datetime = models.DateTimeField(verbose_name='Дата и время обновления')
    type = models.TextField(verbose_name='Тип')
    date = models.DateField(null=True, verbose_name='Дата')
    finished = models.BooleanField(default=True, verbose_name='Закончен')
    error = models.JSONField(null=True, blank=True)


class Account(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    full_name = models.CharField(max_length=128, default='', verbose_name='Название')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Баер')
    fbtool_id = models.PositiveBigIntegerField(verbose_name='Fbtool ID')
    is_deleted = models.BooleanField(default=False)

    access_token = models.TextField(null=True, blank=True)
    cookie = models.JSONField(null=True, blank=True)
    group_id = models.PositiveBigIntegerField(null=True, blank=True)
    group_name = models.TextField(null=True, blank=True)
    is_restricted = models.IntegerField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    proxy = models.IntegerField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    bm_token = models.TextField(null=True, blank=True)
    error = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.buyer.buyer_id} - {self.id}'

    def delete(self):
        self.is_deleted = not self.is_deleted
        self.save()

    @property
    def get_cabinets(self):
        return self.cabinets.select_related().filter(is_deleted=False).order_by('id').order_by('name')

    @property
    def error_cabinets(self):
        return self.get_cabinets.filter(error__isnull=False).exists()

    @property
    def get_deleted_cabinets(self):
        return self.cabinets.select_related().filter(is_deleted=True).order_by('id').order_by('name')

    @property
    def last_update_finished(self):
        update_check = Update.objects.filter(type=f'account-costs-{self.pk}')
        if update_check.exists():
            update = update_check.last()
            if not update.finished and datetime.now() >= update.datetime + timedelta(minutes=5):
                update.finished = True
                update.save()
            return update.finished
        return True

    def update_costs(self, date_start, date_stop, currencies=None):
        if currencies is None:
            currencies = requests.get('https://www.floatrates.com/daily/usd.json').json()
        days = int((date_stop - date_start).days) + 1
        for n in range(days):
            current_date = date_start + timedelta(n)
            update = Update.objects.create(type=f'account-costs-{self.pk}', datetime=datetime.now(), finished=False,
                                           date=current_date)
            response = requests.get(f'https://fbtool.pro/api/get-statistics/?key={config.FBTOOL_KEY}'
                                    f'&account={self.fbtool_id}&dates={current_date}%20-%20{current_date}'
                                    f'&mode=ads&status=all&byDay=1')
            account_data = response.json() if response.status_code == 200 else response.status_code

            if isinstance(account_data, dict) and 'data' in account_data.keys():
                self.error = None
                self.save()

                try:
                    account_data = {a['account_id']: a for a in account_data['data']}

                    cab_response = requests.get(f'https://fbtool.pro/api/get-adaccounts/?key={config.FBTOOL_KEY}'
                                                f'&account={self.fbtool_id}')
                    cab_response_json = cab_response.json() if response.status_code == 200 else {'data': []}

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
                            cab['account'] = self
                            Cabinet.objects.create(**cab)

                    for cabinet in self.get_cabinets:
                        str_cabinet_pk = str(cabinet.pk)
                        if str_cabinet_pk in account_data.keys():
                            cabinet.is_deleted = False
                            cabinet.save()
                            cabinet.update_costs(cabinet_data=account_data[str_cabinet_pk], currencies=currencies)
                        else:
                            cabinet.is_deleted = True
                            cabinet.save()
                except Exception as e:
                    update.error = str(e)
            else:
                self.error = account_data
                self.save()
                update.error = account_data
            update.finished = True
            update.save()

    @classmethod
    def update_accounts(cls):
        update = Update.objects.create(type='accounts', datetime=datetime.now(), finished=False)
        try:
            response = requests.get(f'https://fbtool.pro/api/get-accounts/?key={config.FBTOOL_KEY}')
            if response.status_code == 200:
                response_json = response.json()
            else:
                response_json = {}
                update.error = response.status_code
                update.save()

            accounts = []

            for index, account in response_json.items():
                if index.isdigit():
                    accounts.append(int(account['account_id']))
                    account_check = Account.objects.filter(pk=int(account['account_id']))
                    account['fbtool_id'] = account['id']
                    account['id'] = account['account_id']
                    del account['account_id']

                    buyer_id = account['group_name'].split('_')
                    buyer_id = buyer_id[1] if len(buyer_id) >= 2 else account['group_name']

                    buyer_check = User.objects.filter(buyer_id=buyer_id)
                    if buyer_check.exists():
                        buyer = buyer_check.first()
                    else:
                        password = ''.join(random.sample(list(string.ascii_letters) +
                                                         list(map(lambda x: str(x), range(0, 10))) +
                                                         ['!', '#', '$', '%', '&', '*', '/', ':', ';', '<', '>', '?',
                                                          '@', '^',
                                                          '~'], 10))
                        email = password + '@not.found'
                        buyer = User.objects.create_user(username=email, email=email, password=password)
                        buyer.first_name = 'Not found'
                        buyer.buyer_id = buyer_id
                        buyer.save()

                    account['buyer'] = buyer

                    if account_check.exists():
                        account_obj = account_check.first()
                        account_obj.is_deleted = False
                        for param, value in account.items():
                            setattr(account_obj, param, value)
                        account_obj.save()
                    else:
                        Account.objects.create(**account)
            if accounts:
                for account in Account.objects.filter(is_deleted=False):
                    if account.pk not in accounts:
                        account.is_deleted = True
                        account.save()
        except Exception as e:
            update.error = str(e)

        update.finished = True
        update.save()

    @classmethod
    def last_accounts_update_finished(cls):
        update_check = Update.objects.filter(type='accounts')
        if update_check.exists():
            update = update_check.last()
            if not update.finished and datetime.now() >= update.datetime + timedelta(minutes=5):
                update.finished = True
                update.save()
            return update.finished
        return True


class Cabinet(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=128, verbose_name='Название')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cabinets', verbose_name='Аккаунт')
    timezone = models.CharField(max_length=64, verbose_name='Таймзона')
    currency = models.CharField(max_length=8, verbose_name='Валюта')
    is_deleted = models.BooleanField(default=False)

    status = models.IntegerField(null=True, blank=True)
    adspaymentcycle = models.JSONField(null=True, blank=True)
    adtrust_dsl = models.FloatField(null=True, blank=True)
    amount_spent = models.FloatField(null=True, blank=True)
    current_unbilled_spend = models.JSONField(null=True, blank=True)
    disable_reason = models.IntegerField(null=True, blank=True)
    funding_source_details = models.JSONField(null=True, blank=True)
    fbtool_id = models.TextField(null=True, blank=True)
    is_prepay_account = models.BooleanField(null=True, blank=True)
    next_bill_date = models.DateTimeField(null=True, blank=True)
    owner = models.BigIntegerField(null=True, blank=True)
    prepay_account_balance = models.JSONField(null=True, blank=True)
    spend_cap = models.FloatField(null=True, blank=True)
    timezone_offset_hours_utc = models.IntegerField(null=True, blank=True)
    viewable_business = models.JSONField(null=True, blank=True)
    business = models.JSONField(null=True, blank=True)
    error = models.JSONField(null=True, blank=True)

    def delete(self):
        self.is_deleted = not self.is_deleted
        self.save()

    @property
    def last_update_finished(self):
        update_check = Update.objects.filter(type=f'cabinet-costs-{self.pk}')
        if update_check.exists():
            update = update_check.last()
            if not update.finished and datetime.now() >= update.datetime + timedelta(minutes=5):
                update.finished = True
                update.save()
            return update.finished
        return True

    def update_costs(self, date_start=None, date_stop=None, cabinet_data=None, currencies=None):
        update = Update.objects.create(type=f'cabinet-costs-{self.pk}', datetime=datetime.now(), finished=False)
        try:
            if cabinet_data is None:
                response = requests.get(f'https://fbtool.pro/api/get-statistics/?key={config.FBTOOL_KEY}'
                                        f'&account={self.account.fbtool_id}&dates={date_start}%20-%20{date_stop}'
                                        f'&mode=ads&status=all&byDay=1&ad_account={self.pk}')
                response = response.json() if response.status_code == 200 else response.status_code

                if isinstance(response, dict) and 'data' in response.keys():
                    cabinet_data = response['data'][0]
                else:
                    self.error = response
                    self.save()
                    update.error = response
                    update.save()

            if cabinet_data is not None:
                self.error = None
                self.save()

            if currencies is None:
                currencies = requests.get('https://www.floatrates.com/daily/usd.json').json()
            currency_rate = currencies[self.currency.lower()]['inverseRate'] if not self.currency == 'USD' else 1
            if cabinet_data is not None and 'ads' in cabinet_data.keys():
                updated_campaigns = {}
                updated_adsets = {}
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
                            campaign_data['cabinet'] = self
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
                        for insight in insights:
                            cost_check = Cost.objects.filter(ad__pk=ad.pk, date=insight['date_start'])
                            if not cost_check.exists() or not cost_check.first().definitive:
                                cost_check.delete()
                                actions = []
                                cpat = []

                                if 'actions' in insight.keys():
                                    actions = insight['actions']
                                    del insight['actions']
                                if 'cost_per_action_type' in insight.keys():
                                    cpat = insight['cost_per_action_type']
                                    del insight['cost_per_action_type']

                                insight['ad'] = ad
                                insight['date'] = insight['date_start']
                                insight['amount'] = insight['spend']
                                insight['amount_USD'] = round(float(insight['amount']) * currency_rate,
                                                              2) if self.currency != 'USD' else insight['amount']
                                if (datetime.strptime(insight['date_start'], '%Y-%m-%d').date()
                                        < datetime.now(pytz.timezone(self.timezone)).date()):
                                    insight['definitive'] = True
                                del insight['spend']
                                del insight['date_start']
                                del insight['date_stop']
                                cost = Cost.objects.create(**insight)

                                actions_to_create = {
                                    a['action_type']: {'count': a['value'], 'type': a['action_type'], 'cost': cost}
                                    for a in actions}
                                for action in cpat:
                                    actions_to_create[action['action_type']]['value'] = action['value']

                                for action in actions_to_create.values():
                                    Action.objects.create(**action)
        except Exception as e:
            update.error = str(e)
        update.finished = True
        update.save()


class Campaign(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    effective_status = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name='campaigns', verbose_name='Кабинет')


class AdSet(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    effective_status = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name='Кампания')


class Ad(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    creative = models.JSONField(null=True, blank=True)
    effective_status = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    adset = models.ForeignKey(AdSet, on_delete=models.CASCADE, verbose_name='Адсет')

    def natural_key(self):
        cabinet = self.adset.campaign.cabinet
        buyer = cabinet.account.buyer
        return {'buyer_pk': buyer.pk, "buyer_id": buyer.buyer_id, "cabinet_pk": cabinet.pk, "currency": cabinet.currency}


class Cost(models.Model):

    date = models.DateField(verbose_name='Дата')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='costs', verbose_name='Объявление')
    amount = models.FloatField(verbose_name='Расход')
    amount_USD = models.FloatField(null=True, verbose_name='Расход USD')
    clicks = models.PositiveIntegerField(null=True, blank=True, verbose_name='Клики')
    definitive = models.BooleanField(default=False, verbose_name='Окончательный вариант')
    cost_per_unique_click = models.FloatField(null=True)
    cpc = models.FloatField(null=True)
    cpm = models.FloatField(null=True)
    ctr = models.FloatField(null=True)
    impressions = models.PositiveIntegerField(null=True)
    objective = models.TextField(null=True)
    quality_score_ectr = models.FloatField(null=True)
    quality_score_ecvr = models.FloatField(null=True)
    quality_score_organic = models.FloatField(null=True)
    results = models.JSONField(null=True, blank=True)

    @property
    def get_actions(self):
        return self.actions.select_related()


class Action(models.Model):

    cost = models.ForeignKey(Cost, on_delete=models.CASCADE, related_name='actions', verbose_name='Расход')
    type = models.CharField(max_length=128, verbose_name='Тип')
    count = models.IntegerField(verbose_name='Количество')
    value = models.FloatField(default=0, verbose_name='Стоимость')


class Revenue(models.Model):

    datetime = models.DateTimeField(null=True, verbose_name='Дата и время')
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='revenues', verbose_name='Баер')
    amount = models.FloatField(verbose_name='Доход')
    clicks = models.PositiveIntegerField(null=True, blank=True)
    conversions = models.PositiveIntegerField(null=True, blank=True)
    sales = models.PositiveIntegerField(null=True, blank=True)
    sub_id = models.TextField(null=True, blank=True)
    sub_id_1 = models.TextField(null=True, blank=True)
    sub_id_2 = models.TextField(null=True, blank=True)
    sub_id_3 = models.TextField(null=True, blank=True)
    sub_id_5 = models.TextField(null=True, blank=True)
    sub_id_6 = models.TextField(null=True, blank=True)
    sub_id_7 = models.TextField(null=True, blank=True)
    sub_id_8 = models.TextField(null=True, blank=True)
    sub_id_9 = models.TextField(null=True, blank=True)
    sub_id_10 = models.TextField(null=True, blank=True)
    sub_id_11 = models.TextField(null=True, blank=True)
    sub_id_12 = models.TextField(null=True, blank=True)
    campaign = models.TextField(null=True, blank=True)
    campaign_group = models.TextField(null=True, blank=True)
    campaign_id = models.PositiveIntegerField(null=True, blank=True)
    campaign_unique_clicks = models.PositiveIntegerField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    country_code = models.TextField(null=True, blank=True)
    offer = models.TextField(null=True, blank=True)
    os_icon = models.TextField(null=True, blank=True)
    os_version = models.TextField(null=True, blank=True)
    definitive = models.BooleanField(default=False, verbose_name='Окончательный вариант')


@receiver(models.signals.post_save, sender=Cabinet)
def update_costs_signal(sender, instance, created, **kwargs):
    if created:
        date_stop = datetime.now().date()
        date_start = date_stop - timedelta(days=30)
        instance.update_costs(date_start, date_stop)
