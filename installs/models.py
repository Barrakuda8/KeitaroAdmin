from django.db import models
from authapp.models import User


class Application(models.Model):

    name = models.TextField(null=True, blank=True, verbose_name='Название')
    key_id = models.TextField(null=True, blank=True, verbose_name='Key ID')
    team_id = models.TextField(null=True, blank=True, verbose_name='Team ID')
    key = models.FileField(upload_to='keys/', verbose_name='Key')
    bundle = models.TextField(null=True, blank=True, unique=True, verbose_name='Бандл')
    is_deleted = models.BooleanField(default=False)

    def delete(self):
        self.is_deleted = not self.is_deleted
        self.save()


class Install(models.Model):

    external_id = models.TextField(unique=True, primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='installs')
    application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True, related_name='installs')
    status = models.CharField(max_length=64, default='Install')
    campaign = models.TextField(null=True, blank=True)
    campaign_id = models.PositiveIntegerField(null=True, blank=True)
    stream = models.TextField(null=True, blank=True)
    stream_id = models.PositiveIntegerField(null=True, blank=True)
    campaign_unique_clicks = models.PositiveIntegerField(null=True, blank=True)
    conversions = models.PositiveIntegerField(null=True, blank=True)
    country_flag = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    ip = models.TextField(null=True, blank=True)
    language = models.TextField(null=True, blank=True)
    os = models.TextField(null=True, blank=True)
    os_version = models.TextField(null=True, blank=True)
    sales = models.PositiveIntegerField(null=True, blank=True)
    revenue = models.FloatField(null=True, blank=True)
    sub_id = models.TextField(null=True, blank=True)
    sub_id_1 = models.TextField(null=True, blank=True)
    sub_id_2 = models.TextField(null=True, blank=True)
    sub_id_3 = models.TextField(null=True, blank=True)
    sub_id_5 = models.TextField(null=True, blank=True)
    sub_id_6 = models.TextField(null=True, blank=True)
    sub_id_7 = models.TextField(null=True, blank=True)
    sub_id_8 = models.TextField(null=True, blank=True)
    sub_id_9 = models.TextField(null=True, blank=True)
    sub_id_10 = models.TextField(null=True, blank=True)
    sub_id_11 = models.TextField(null=True, blank=True)
    sub_id_12 = models.TextField(null=True, blank=True)
    sub_id_13 = models.TextField(null=True, blank=True)
    sub_id_14 = models.TextField(null=True, blank=True)
    sub_id_15 = models.TextField(null=True, blank=True)
    sub_id_16 = models.TextField(null=True, blank=True)
    sub_id_17 = models.TextField(null=True, blank=True)
    sub_id_18 = models.TextField(null=True, blank=True)
    sub_id_19 = models.TextField(null=True, blank=True)
    sub_id_20 = models.TextField(null=True, blank=True)
    sub_id_21 = models.TextField(null=True, blank=True)
    sub_id_22 = models.TextField(null=True, blank=True)
    sub_id_23 = models.TextField(null=True, blank=True)
    sub_id_24 = models.TextField(null=True, blank=True)
    sub_id_25 = models.TextField(null=True, blank=True)
    sub_id_26 = models.TextField(null=True, blank=True)
    sub_id_27 = models.TextField(null=True, blank=True)
    sub_id_28 = models.TextField(null=True, blank=True)
    sub_id_29 = models.TextField(null=True, blank=True)
    sub_id_30 = models.TextField(null=True, blank=True)


class Push(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now=True)
    title = models.TextField(null=True)
    text = models.TextField(null=True)
    launch_image = models.ImageField(upload_to='launch_images', null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    offers = models.TextField(null=True, blank=True)
    country_flags = models.TextField(null=True, blank=True)
    applications = models.TextField(null=True, blank=True)
    buyers = models.TextField(null=True, blank=True)
    statuses = models.TextField(null=True, blank=True)
