# Generated by Django 5.0.6 on 2024-07-18 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0003_user_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='app_admin',
            field=models.BooleanField(default=False),
        ),
    ]