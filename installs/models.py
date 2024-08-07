import asyncio
import json
import random
import string
from datetime import datetime, timedelta
from pprint import pprint

import requests
from django.db import models
from kalyke import ApnsClient, PayloadAlert, Payload, ApnsConfig
from kalyke.exceptions import BadDeviceToken

import config
from authapp.models import User


class Application(models.Model):

    name = models.TextField(null=True, blank=True, verbose_name='Название')
    key_id = models.TextField(null=True, blank=True, verbose_name='Key ID')
    team_id = models.TextField(null=True, blank=True, verbose_name='Team ID')
    key = models.FileField(upload_to='keys/', verbose_name='Key')
    bundle = models.TextField(null=True, blank=True, unique=True, verbose_name='Бандл')
    campaign_id = models.PositiveIntegerField(null=True, verbose_name='ID Кампании')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def delete(self):
        self.is_deleted = not self.is_deleted
        self.save()

    def get_installs(self, time_from, time_to):
        payload = json.dumps({
            "range": {
                "interval": "custom_time_range",
                "timezone": config.TIMEZONE,
                "from": ":".join(str(time_from).split(':')[:2]),
                "to": ":".join(str(time_to).split(':')[:2])
            },
            "columns": [],
            "metrics": ["campaign_unique_clicks", "conversions", "sales", "revenue"],
            "grouping": ["datetime", "campaign", "stream", "stream_id", "sub_id", "country_flag", "language", "ip",
                         "os", "os_version", "sub_id_1", "sub_id_2", "sub_id_3", "sub_id_4", "sub_id_5", "sub_id_6",
                         "sub_id_7", "sub_id_8", "sub_id_9", "sub_id_10", "sub_id_11", "sub_id_12", "sub_id_13",
                         "sub_id_14", "sub_id_15", "sub_id_16", "sub_id_17", "sub_id_18", "sub_id_19", "sub_id_20",
                         "sub_id_21", "sub_id_22", "sub_id_23", "sub_id_24", "sub_id_25", "sub_id_26", "sub_id_27",
                         "sub_id_28", "sub_id_29", "sub_id_30", "external_id"],
            "filters": [
                {"name": "campaign_id", "operator": "EQUALS", "expression": self.campaign_id}
            ],
            "sort": [{"name": "sub_id_10", "order": "desc"}],
            "summary": True,
            "offset": 0
        })

        headers = {
            'Api-Key': config.KEITARO_API_KEY,
            'Content-Type': "application/json",
        }
        response = requests.post(url=f'{config.KEITARO_API_URL}/admin_api/v1/report/build',
                                 headers=headers,
                                 data=payload)
        response_json = response.json()

        for data in response_json['rows']:
            if not Install.objects.filter(external_id=data['external_id']).exists():
                if 'sub_id_4' in data.keys():
                    if data['sub_id_4']:
                        buyer_check = User.objects.filter(buyer_id=data['sub_id_4'])
                        if buyer_check.exists():
                            buyer = buyer_check.first()
                        else:
                            password = ''.join(random.sample(list(string.ascii_letters) +
                                                             list(map(lambda x: str(x), range(0, 10))) +
                                                             ['!', '#', '$', '%', '&', '*', '/', ':', ';', '<', '>', '?', '@',
                                                              '^',
                                                              '~'], 10))
                            email = password + '@not.found'
                            buyer = User.objects.create_user(username=email, email=email, password=password)
                            buyer.first_name = 'Not found'
                            buyer.buyer_id = data['sub_id_4']
                            buyer.save()
                        data['buyer'] = buyer
                    del data['sub_id_4']

                data['sub_id_10'] = self.bundle
                data['application'] = self

                Install.objects.create(**data)


class Install(models.Model):

    external_id = models.TextField(unique=True, primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='installs')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, related_name='installs')
    status = models.CharField(max_length=16, default='install')
    registered_at = models.DateTimeField(null=True, blank=True)
    purchased_at = models.DateTimeField(null=True, blank=True)
    campaign = models.TextField(null=True, blank=True)
    campaign_id = models.PositiveIntegerField(null=True, blank=True)
    stream = models.TextField(null=True, blank=True)
    stream_id = models.PositiveIntegerField(null=True, blank=True)
    campaign_unique_clicks = models.PositiveIntegerField(null=True, blank=True)
    conversions = models.PositiveIntegerField(null=True, blank=True)
    country_flag = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    ip = models.TextField(null=True, blank=True)
    language = models.TextField(null=True, blank=True)
    os = models.TextField(null=True, blank=True)
    os_version = models.TextField(null=True, blank=True)
    sales = models.PositiveIntegerField(null=True, blank=True)
    revenue = models.FloatField(null=True, blank=True)
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
    sub_id_13 = models.TextField(null=True, blank=True)
    sub_id_14 = models.TextField(null=True, blank=True)
    sub_id_15 = models.TextField(null=True, blank=True)
    sub_id_16 = models.TextField(null=True, blank=True)
    sub_id_17 = models.TextField(null=True, blank=True)
    sub_id_18 = models.TextField(null=True, blank=True)
    sub_id_19 = models.TextField(null=True, blank=True)
    sub_id_20 = models.TextField(null=True, blank=True)
    sub_id_21 = models.TextField(null=True, blank=True)
    sub_id_22 = models.TextField(null=True, blank=True)
    sub_id_23 = models.TextField(null=True, blank=True)
    sub_id_24 = models.TextField(null=True, blank=True)
    sub_id_25 = models.TextField(null=True, blank=True)
    sub_id_26 = models.TextField(null=True, blank=True)
    sub_id_27 = models.TextField(null=True, blank=True)
    sub_id_28 = models.TextField(null=True, blank=True)
    sub_id_29 = models.TextField(null=True, blank=True)
    sub_id_30 = models.TextField(null=True, blank=True)


class Push(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=16, default='normal', verbose_name='Тип')
    created_at = models.DateTimeField(auto_now=True)
    title = models.TextField(null=True, blank=True, verbose_name='Заголовок')
    text = models.TextField(null=True, blank=True, verbose_name='Текст')
    launch_image = models.ImageField(upload_to='launch_images', null=True, blank=True, verbose_name='Иконка')
    languages = models.TextField(null=True, blank=True)
    offers = models.TextField(null=True, blank=True)
    country_flags = models.TextField(null=True, blank=True)
    applications = models.TextField(null=True, blank=True)
    buyers = models.TextField(null=True, blank=True)
    statuses = models.TextField(null=True, blank=True)
    days = models.CharField(max_length=32, null=True, blank=True)
    hours = models.CharField(max_length=128, blank=True)
    timedelta = models.FloatField(null=True, blank=True, verbose_name='Через какое время (в минутах)')

    def __str__(self):
        return f'{self.created_at.replace(microsecond=0)} - {self.title}'

    @property
    def get_type(self):
        data = {
            'normal': 'Разовый',
            'status': 'По событию',
            'timed': 'По времени'
        }
        return data[self.type]

    @property
    def get_buyers(self):
        return ', '.join(map(lambda x: str(x),
                             User.objects.filter(pk__in=map(lambda x: int(x), self.buyers.split(', ')))))

    @property
    def get_applications(self):
        return ', '.join(map(lambda x: str(x),
                             Application.objects.filter(pk__in=map(lambda x: int(x), self.applications.split(', ')))))

    @property
    def get_languages(self):
        return self.languages.split(', ')

    def send(self, now=None, data=None):
        installs = Install.objects.filter(application__isnull=False, application__is_deleted=False,
                                          application__key_id__isnull=False, application__team_id__isnull=False,
                                          application__key__isnull=False)
        if not self.user or self.user.is_superuser or self.user.app_admin:
            pass
        elif self.user.lead:
            installs = installs.filter(buyer__team__pk=self.user.team.pk)
        else:
            installs = installs.filter(buyer__pk=self.user.pk)
        if self.languages:
            languages = data['languages'] if data is not None else self.languages.split(', ')
            installs = installs.filter(language__in=languages)
        if self.country_flags:
            country_flags = data['country_flags'] if data is not None else self.country_flags.split(', ')
            installs = installs.filter(country_flag__in=country_flags)
        if self.offers:
            offers = data['offers'] if data is not None else self.offers.split(', ')
            installs = installs.filter(sub_id_2__in=offers)
        if self.applications:
            applications = data['applications'] if data is not None else self.applications.split(', ')
            installs = installs.filter(application__pk__in=map(lambda x: int(x), applications))
        if self.buyers:
            buyers = data['buyers'] if data is not None else self.buyers.split(', ')
            installs = installs.filter(buyer__pk__in=map(lambda x: int(x), buyers))
        if self.type == 'status':
            time = now - timedelta(minutes=self.timedelta)
            start = time.replace(second=0)
            stop = time.replace(second=59)
            if self.statuses == 'reg':
                installs = installs.filter(status='reg', registered_at__gte=start, registered_at__lte=stop)
            if self.statuses == 'dep':
                installs = installs.filter(status='dep', purchased_at__gte=start, purchased_at__lte=stop)
        elif self.statuses:
            statuses = data['statuses'] if data is not None else self.statuses.split(', ')
            installs = installs.filter(status__in=statuses)

        applications = installs.values_list('application__pk').distinct()

        for app_pk in applications:
            application = Application.objects.get(pk=app_pk[0])
            client = ApnsClient(
                use_sandbox=False,
                team_id=application.team_id,
                auth_key_id=application.key_id,
                auth_key_filepath=application.key.path,
            )
            payload_alert = PayloadAlert(title=self.title, body=self.text, launch_image=self.launch_image.url) \
                if self.launch_image else PayloadAlert(title=self.title, body=self.text)
            payload = Payload(alert=payload_alert, badge=1, sound="default")
            config_ = ApnsConfig(topic=application.bundle)
            app_installs = installs.filter(application__pk=app_pk[0])

            for install in app_installs:
                try:
                    asyncio.run(
                        client.send_message(
                            device_token=install.external_id,
                            payload=payload,
                            apns_config=config_,
                        )
                    )
                except BadDeviceToken:
                    pass
