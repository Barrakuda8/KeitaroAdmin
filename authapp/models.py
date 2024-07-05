from django.db import models
from django.contrib.auth.models import AbstractUser


class Team(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Название')

    def __str__(self):
        return self.name

    @property
    def get_users(self):
        return self.users.select_related().order_by('lead').order_by('buyer_id')


class User(AbstractUser):

    email = models.EmailField(unique=True, verbose_name='Адрес электронной почты')
    lead = models.BooleanField(default=False, verbose_name='Лид')
    support_id = models.CharField(max_length=8, null=True, blank=True, unique=True, verbose_name='ID Саппорта')
    buyer_id = models.CharField(max_length=8, null=True, blank=True, unique=True, verbose_name='ID Баера')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='users', null=True, blank=True, verbose_name='Команда')

    def __str__(self):
        return f'{self.buyer_id} - {self.first_name}'

    def natural_key(self):
        return self.pk, self.buyer_id
