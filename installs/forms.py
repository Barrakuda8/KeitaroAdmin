from django import forms

from installs.models import Application


class AppEditForm(forms.ModelForm):

    class Meta:
        model = Application
        exclude = ('is_deleted',)

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.help_text = ''