# Generated by Django 5.0.6 on 2024-07-31 16:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0024_update_date_alter_update_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='cost',
            name='campaign',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='adminapp.campaign', verbose_name='Кампания'),
        ),
        migrations.AlterField(
            model_name='cost',
            name='ad',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='adminapp.ad', verbose_name='Объявление'),
        ),
    ]
