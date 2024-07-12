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
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.buyer_id:
            return f'{self.buyer_id} - {self.first_name}'
        elif self.support_id:
            return f'{self.support_id} - {self.first_name}'
        else:
            return self.first_name

    def delete(self):
        if self.buyer_id:
            if not self.is_deleted:
                self.is_deleted = True
                self.team = None
                self.save()
            else:
                self.is_deleted = False
                self.save()
        else:
            super(User, self).delete()

    def natural_key(self):
        return self.pk, self.buyer_id
