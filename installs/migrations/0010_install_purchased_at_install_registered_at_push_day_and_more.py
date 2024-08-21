# Generated by Django 5.0.6 on 2024-08-05 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installs', '0009_remove_push_os_versions_push_applications_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='install',
            name='purchased_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='install',
            name='registered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='day',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='timedelta',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='type',
            field=models.CharField(default='normal', max_length=16),
        ),
        migrations.AlterField(
            model_name='install',
            name='status',
            field=models.CharField(default='install', max_length=16),
        ),
    ]