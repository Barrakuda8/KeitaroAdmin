from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django import forms
from .models import User, Team


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Логин'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль'


class UserCreateForm(UserCreationForm):
    buyer_id = forms.CharField(max_length=8, required=True, label='ID Баера')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'lead', 'buyer_id', 'team')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.username = user.email
        user.save()

        return user


class UserEditForm(UserChangeForm):
    buyer_id = forms.CharField(max_length=8, required=True, label='ID Баера')
    password = None

    class Meta:
        model = User
        fields = ('email', 'first_name', 'lead', 'buyer_id', 'team')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.username = user.email
        user.save()

        return user


class SupportCreateForm(UserCreationForm):
    support_id = forms.CharField(max_length=8, required=True, label='ID Саппорта')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'support_id', 'app_admin')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.username = user.email
        user.save()

        return user


class SupportEditForm(UserChangeForm):
    support_id = forms.CharField(max_length=8, required=True, label='ID Саппорта')
    password = None

    class Meta:
        model = User
        fields = ('email', 'first_name', 'support_id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.username = user.email
        user.save()

        return user


class TeamEditForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''
