import json
import random
import string
from datetime import datetime, timedelta
from pprint import pprint

import pytz
import requests
from django.core.management import BaseCommand

import config
from adminapp.models import Revenue, Update
from authapp.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        day = "yesterday" if datetime.now().hour == 0 else "today"
        payload = json.dumps(
            {"range": {"interval": day, "timezone": "Europe/Moscow"}, "columns": [],
             "metrics": ["clicks", "campaign_unique_clicks", "conversions", "sales", "revenue"],
             "grouping": ["datetime", "campaign", "campaign_group", "os_icon", "os_version", "country", "offer",
                          "sub_id_1",
                          "sub_id_2", "sub_id_3", "sub_id_4", "sub_id_5", "sub_id_6", "sub_id_7", "sub_id_8",
                          "sub_id_9",
                          "sub_id_10", "sub_id_11", "sub_id_12", "sub_id"],
             "filters": [{"name": "offer_id", "operator": "NOT_EQUAL", "expression": ""}],
             "summary": True,
             "offset": 0}
        )

        headers = {
            'Api-Key': config.KEITARO_API_KEY,
            'Content-Type': "application/json",
        }
        response = requests.post(url=f'{config.KEITARO_API_URL}/admin_api/v1/report/build',
                                 headers=headers,
                                 data=payload)
        response_json = response.json()

        for revenue_data in response_json['rows']:
            if revenue_data['sub_id_9'].isdigit() and len(revenue_data['sub_id_10']) > 10:
                if not Revenue.objects.filter(sub_id=revenue_data['sub_id']).exists():
                    revenue_data['amount'] = revenue_data['revenue']
                    del revenue_data['revenue']
                    buyer_check = User.objects.filter(buyer_id=revenue_data['sub_id_4'])
                    if buyer_check.exists():
                        buyer = buyer_check.first()
                    else:
                        password = ''.join(random.sample(list(string.ascii_letters) +
                                                         list(map(lambda x: str(x), range(0,10))) +
                                                         ['!', '#', '$', '%', '&', '*', '/', ':', ';', '<', '>', '?', '@', '^', '~'], 10))
                        email = password + '@not.found'
                        buyer = User.objects.create_user(username=email, email=email, password=password)
                        buyer.first_name = 'Not found'
                        buyer.buyer_id = revenue_data['sub_id_4']
                        buyer.save()

                    del revenue_data['sub_id_4']
                    revenue_data['buyer'] = buyer
                    revenue_data['datetime'] = (datetime.strptime(revenue_data['datetime'], '%Y-%m-%d %H:%M:%S'))
                    if day == 'yesterday':
                        revenue_data['definitive'] = True
                    Revenue.objects.create(**revenue_data)

        Update.objects.create(type='revenues', datetime=datetime.now())
