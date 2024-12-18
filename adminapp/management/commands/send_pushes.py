from datetime import datetime, timedelta

import pytz
from django.core.management import BaseCommand

import config
from installs.models import Push


class Command(BaseCommand):

    def handle(self, *args, **options):
        now = datetime.now(pytz.timezone(config.TIMEZONE)).replace(microsecond=0)
        if now.minute == 0:
            day = now.weekday()
            hour = now.hour
            timed_pushes = Push.objects.filter(type='timed', days__contains=f'{day}|', hours=f'{hour}|')
            for push in timed_pushes:
                with open('send_pushes.txt', 'a') as f:
                    f.write(f'{now} - {push.pk} - timed\n')
                push.send()

        status_pushes = Push.objects.filter(type='status')
        for push in status_pushes:
            with open('send_pushes.txt', 'a') as f:
                f.write(f'{now} - {push.pk} - status\n')
            push.send(now=now)
