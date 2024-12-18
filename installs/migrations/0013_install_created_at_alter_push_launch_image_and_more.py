# Generated by Django 5.0.6 on 2024-08-19 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installs', '0012_application_campaign_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='install',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='push',
            name='launch_image',
            field=models.ImageField(blank=True, null=True, upload_to='launch_images', verbose_name='Иконка'),
        ),
        migrations.AlterField(
            model_name='push',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='push',
            name='timedelta',
            field=models.FloatField(blank=True, null=True, verbose_name='Через какое время (в минутах)'),
        ),
        migrations.AlterField(
            model_name='push',
            name='title',
            field=models.TextField(blank=True, null=True, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='push',
            name='type',
            field=models.CharField(default='normal', max_length=16, verbose_name='Тип'),
        ),
    ]
