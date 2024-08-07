from django import forms
from django.db.models import Q

from authapp.models import User
from installs.models import Application, Push, Install


class AppEditForm(forms.ModelForm):

    class Meta:
        model = Application
        exclude = ('is_deleted',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''


class StatusPushEditForm(forms.ModelForm):

    STATUSES = (
        ('install', 'Install'),
        ('reg', 'Registration'),
        ('dep', 'Deposit')
    )

    buyers = forms.MultipleChoiceField(choices=(), required=False, label='Баеры')
    applications = forms.MultipleChoiceField(choices=(), required=False, label='Приложения')
    languages = forms.MultipleChoiceField(choices=(), required=False, label='Language')
    offers = forms.MultipleChoiceField(choices=(), required=False, label='Offer')
    country_flags = forms.MultipleChoiceField(choices=(), required=False, label='Country flag')
    statuses = forms.ChoiceField(choices=STATUSES, label='Статус')
    user = forms.ModelChoiceField(queryset=None, disabled=True, label='Пользователь')

    class Meta:
        model = Push
        exclude = ('days', 'hours')

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        installs = Install.objects.filter(application__isnull=False, application__is_deleted=False,
                                          application__key_id__isnull=False, application__team_id__isnull=False,
                                          application__key__isnull=False)

        user = User.objects.get(pk=user_id)

        if user.is_superuser or user.app_admin:
            pass
        elif user.lead:
            installs = Install.objects.filter(buyer__team__pk=user.team.pk)
        else:
            installs = Install.objects.filter(buyer__pk=user.pk)
            self.fields['buyers'].widget.attrs['class'] = 'form-input-invisible'

        self.fields['buyers'].choices = ((x.pk, str(x)) for x in
                                         User.objects.filter(pk__in=installs.values_list('buyer__pk').distinct()))
        self.fields['languages'].choices = ((x[0], x[0]) for x in
                                            installs.filter(language__isnull=False)
                                            .order_by('language').values_list('language').distinct())
        self.fields['country_flags'].choices = ((x[0], x[0]) for x in
                                                installs.filter(country_flag__isnull=False)
                                                .order_by('country_flag').values_list('country_flag').distinct())
        self.fields['applications'].choices = ((x.pk, x.name) for x in
                                               Application.objects.filter(
                                                   pk__in=installs.values_list('application__pk').distinct()))
        self.fields['offers'].choices = ((x[0], x[0]) for x in
                                         installs.filter(Q(sub_id_2__isnull=False), ~Q(sub_id_2=''))
                                         .order_by('sub_id_2').values_list('sub_id_2').distinct())
        self.fields['user'].queryset = User.objects.filter(pk=user_id)

        for field_name, field in self.fields.items():
            if field_name in ['languages', 'country_flags', 'offers', 'buyers', 'applications']:
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-input'
            field.help_text = ''
            if field_name in ['user', 'type']:
                field.widget.attrs['readonly'] = True

    def save(self, *args, **kwargs):
        push = super().save(*args, **kwargs)
        push.languages = None if not push.languages else ', '.join(eval(push.languages))
        push.country_flags = None if not push.country_flags else ', '.join(eval(push.country_flags))
        push.offers = None if not push.offers else ', '.join(eval(push.offers))
        push.buyers = None if not push.buyers else ', '.join(eval(push.buyers))
        push.applications = None if not push.applications else ', '.join(eval(push.applications))
        push.statuses = eval(push.statuses)[0]
        push.save()
        return push


class TimedPushEditForm(forms.ModelForm):

    buyers = forms.MultipleChoiceField(choices=(), required=False, label='Баеры')
    applications = forms.MultipleChoiceField(choices=(), required=False, label='Приложения')
    languages = forms.MultipleChoiceField(choices=(), required=False, label='Language')
    offers = forms.MultipleChoiceField(choices=(), required=False, label='Offer')
    country_flags = forms.MultipleChoiceField(choices=(), required=False, label='Country flag')
    statuses = forms.MultipleChoiceField(choices=(), required=False, label='Статусы')
    user = forms.ModelChoiceField(queryset=None, disabled=True, label='Пользователь')

    class Meta:
        model = Push
        exclude = ('timedelta',)

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        installs = Install.objects.filter(application__isnull=False, application__is_deleted=False,
                                          application__key_id__isnull=False, application__team_id__isnull=False,
                                          application__key__isnull=False)

        user = User.objects.get(pk=user_id)

        if user.is_superuser or user.app_admin:
            pass
        elif user.lead:
            installs = Install.objects.filter(buyer__team__pk=user.team.pk)
        else:
            installs = Install.objects.filter(buyer__pk=user.pk)
            self.fields['buyers'].widget.attrs['class'] = 'form-input-invisible'

        self.fields['buyers'].choices = ((x.pk, str(x)) for x in
                                          User.objects.filter(pk__in=installs.values_list('buyer__pk').distinct()))
        self.fields['languages'].choices = ((x[0], x[0]) for x in
                                            installs.filter(language__isnull=False)
                                            .order_by('language').values_list('language').distinct())
        self.fields['country_flags'].choices = ((x[0], x[0]) for x in
                                                installs.filter(country_flag__isnull=False)
                                                .order_by('country_flag').values_list('country_flag').distinct())
        self.fields['applications'].choices = ((x.pk, x.name) for x in
                                               Application.objects.filter(
                                                   pk__in=installs.values_list('application__pk').distinct()))
        self.fields['offers'].choices = ((x[0], x[0]) for x in
                                         installs.filter(Q(sub_id_2__isnull=False), ~Q(sub_id_2=''))
                                         .order_by('sub_id_2').values_list('sub_id_2').distinct())
        self.fields['statuses'].choices = ((x[0], x[0]) for x in
                                           installs.filter(status__isnull=False)
                                           .order_by('status').values_list('status').distinct())
        self.fields['user'].queryset = User.objects.filter(pk=user_id)

        for field_name, field in self.fields.items():
            if field_name in ['languages', 'country_flags', 'offers', 'statuses', 'buyers', 'applications']:
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-input'
            field.help_text = ''
            if field_name in ['user', 'type']:
                field.widget.attrs['readonly'] = True
            if field_name in ['days', 'hours']:
                field.widget.attrs['style'] = 'display: none;'

    def save(self, *args, **kwargs):
        push = super().save(*args, **kwargs)
        push.languages = None if not push.languages else ', '.join(eval(push.languages))
        push.country_flags = None if not push.country_flags else ', '.join(eval(push.country_flags))
        push.offers = None if not push.offers else ', '.join(eval(push.offers))
        push.buyers = None if not push.buyers else ', '.join(eval(push.buyers))
        push.applications = None if not push.applications else ', '.join(eval(push.applications))
        push.statuses = None if not push.statuses else ', '.join(eval(push.statuses))
        push.save()
        return push
