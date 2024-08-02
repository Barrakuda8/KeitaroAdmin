from datetime import datetime, timedelta
import requests
from django.core.management import BaseCommand

import config
from adminapp.models import Account, Update


class Command(BaseCommand):

    def handle(self, *args, **options):
        update = Update.objects.create(type='costs')
        currencies = requests.get('https://www.floatrates.com/daily/usd.json').json()

        Account.update_accounts()

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        accounts = Account.objects.filter(is_deleted=False)
        for account in accounts:
            account.update_costs(yesterday, tomorrow, currencies)

        update.finished = True
        update.save()

