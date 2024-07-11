from datetime import datetime, timedelta
import requests
from django.core.management import BaseCommand
from adminapp.models import Account, Update


class Command(BaseCommand):

    def handle(self, *args, **options):
        update = Update.objects.create(type='costs', datetime=datetime.now(), finished=False)
        currencies = requests.get('https://www.floatrates.com/daily/usd.json').json()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        accounts = Account.objects.all()
        for account in accounts:
            account.update_costs(yesterday, tomorrow, currencies)

        update.finished = True
        update.save()

