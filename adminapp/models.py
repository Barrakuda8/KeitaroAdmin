from datetime import datetime, timedelta

from django.db import models
from authapp.models import User


class Update(models.Model):

    datetime = models.DateTimeField(verbose_name='Дата и время')
    type = models.TextField(verbose_name='Тип')
    finished = models.BooleanField(default=True, verbose_name='Закончен')


class Account(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    full_name = models.CharField(max_length=128, default='', verbose_name='Название')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Баер')
    fbtool_id = models.PositiveBigIntegerField(verbose_name='Fbtool ID')

    access_token = models.TextField(null=True, blank=True)
    cookie = models.JSONField(null=True, blank=True)
    group_id = models.PositiveBigIntegerField(null=True, blank=True)
    group_name = models.TextField(null=True, blank=True)
    is_restricted = models.IntegerField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    proxy = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.buyer.buyer_id} - {self.id}'

    @property
    def get_cabinets(self):
        return self.cabinets.select_related().order_by('id').order_by('name')


class Cabinet(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=128, verbose_name='Название')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cabinets', verbose_name='Аккаунт')
    timezone = models.CharField(max_length=64, verbose_name='Таймзона')
    currency = models.CharField(max_length=8, verbose_name='Валюта')
    is_deleted = models.BooleanField(default=False, verbose_name='Кабинет удалён')

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

    @property
    def last_update_finished(self):
        update_check = Update.objects.filter(type=f'cabinet-costs-{self.pk}')
        if update_check.exists():
            update = update_check.last()
            if not update.finished and datetime.now() >= update.datetime + timedelta(minutes=1):
                update.finished = True
                update.save()
            print(update.finished)
            return update.finished
        return True


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
