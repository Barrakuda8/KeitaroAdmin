# Generated by Django 5.0.6 on 2024-07-26 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installs', '0008_install_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='push',
            name='os_versions',
        ),
        migrations.AddField(
            model_name='push',
            name='applications',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='buyers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='offers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='push',
            name='statuses',
            field=models.TextField(blank=True, null=True),
        ),
    ]
