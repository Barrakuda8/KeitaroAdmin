# Generated by Django 5.0.6 on 2024-07-01 14:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cost',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costs', to='adminapp.ad', verbose_name='Объявление'),
        ),
    ]
