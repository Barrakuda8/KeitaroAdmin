from django import forms
from adminapp.models import Account, Cabinet
from authapp.models import User


class AccountEditForm(forms.ModelForm):

    buyer = forms.ModelChoiceField(queryset=None, empty_label=None, label='Баер')

    class Meta:
        model = Account
        fields = '__all__'

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        user = User.objects.get(pk=user_id)
        if user.is_superuser:
            queryset = User.objects.filter(buyer_id__isnull=False)
        elif user.lead:
            queryset = User.objects.filter(team__pk=user.team.pk)
        else:
            queryset = User.objects.filter(pk=user_id)
            self.fields['buyer'].widget.attrs['class'] = 'form-input-invisible'

        self.fields['buyer'].queryset = queryset
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''


class CabinetEditForm(forms.ModelForm):

    account = forms.ModelChoiceField(queryset=None, empty_label=None, label='Аккаунт')

    class Meta:
        model = Cabinet
        fields = '__all__'

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        user = User.objects.get(pk=user_id)
        if user.is_superuser:
            queryset = Account.objects.all()
        elif user.lead:
            queryset = Account.objects.filter(buyer__team__pk=user.team.pk)
        else:
            queryset = Account.objects.filter(buyer__pk=user_id)

        self.fields['account'].queryset = queryset
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''