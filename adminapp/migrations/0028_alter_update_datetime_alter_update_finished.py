# Generated by Django 5.0.6 on 2024-08-02 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0027_alter_requestsperminute_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='update',
            name='datetime',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата и время обновления'),
        ),
        migrations.AlterField(
            model_name='update',
            name='finished',
            field=models.BooleanField(default=False, verbose_name='Закончен'),
        ),
    ]