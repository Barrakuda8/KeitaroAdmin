from datetime import datetime, timedelta

from django.core.management import BaseCommand
from installs.models import Application


class Command(BaseCommand):

    def handle(self, *args, **options):
        time_to = datetime.now().replace(microsecond=0, second=0)
        time_from = time_to - timedelta(days=30)

        applications = Application.objects.filter(is_deleted=False)
        for app in applications:
            app.get_installs(time_from, time_to)