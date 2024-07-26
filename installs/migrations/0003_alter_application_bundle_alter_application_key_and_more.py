# Generated by Django 5.0.6 on 2024-07-18 23:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installs', '0002_application'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='bundle',
            field=models.TextField(blank=True, null=True, verbose_name='Бандл'),
        ),
        migrations.AlterField(
            model_name='application',
            name='key',
            field=models.FileField(upload_to='keys/', verbose_name='Key'),
        ),
        migrations.AlterField(
            model_name='application',
            name='key_id',
            field=models.TextField(blank=True, null=True, verbose_name='Key ID'),
        ),
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.TextField(blank=True, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='application',
            name='team_id',
            field=models.TextField(blank=True, null=True, verbose_name='Team ID'),
        ),
        migrations.CreateModel(
            name='Push',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('languages', models.TextField(blank=True, null=True)),
                ('os_versions', models.TextField(blank=True, null=True)),
                ('country_flags', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
