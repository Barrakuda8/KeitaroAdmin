from datetime import datetime, timedelta
from django.core.management import BaseCommand
from installs.models import Push


class Command(BaseCommand):

    def handle(self, *args, **options):
        now = datetime.now().replace(microsecond=0) + timedelta(minutes=1)
        if now.minute == 0:
            day = now.weekday()
            hour = now.hour
            timed_pushes = Push.objects.filter(type='timed', days__contains=f'{day}|', hours=f'{hour}|')
            for push in timed_pushes:
                push.send()

        status_pushes = Push.objects.filter(type='status')
        for push in status_pushes:
            push.send(now=now)
