# Generated by Django 5.0.6 on 2024-07-11 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0018_cabinet_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='error',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
