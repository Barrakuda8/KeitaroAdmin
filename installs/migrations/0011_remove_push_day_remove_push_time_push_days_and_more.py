# Generated by Django 5.0.6 on 2024-08-06 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installs', '0010_install_purchased_at_install_registered_at_push_day_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='push',
            name='day',
        ),
        migrations.RemoveField(
            model_name='push',
            name='time',
        ),
        migrations.AddField(
            model_name='push',
            name='days',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='hours',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
