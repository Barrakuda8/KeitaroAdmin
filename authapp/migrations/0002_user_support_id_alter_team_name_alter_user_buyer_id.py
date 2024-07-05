# Generated by Django 5.0.6 on 2024-07-05 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='support_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True, verbose_name='ID Саппорта'),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=32, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='user',
            name='buyer_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True, verbose_name='ID Баера'),
        ),
    ]