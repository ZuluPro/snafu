from django.contrib.auth.models import User
from django import forms
from django.forms import widgets, formsets

from referentiel.models import *
from sendim.models import *

class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        widgets = {
            'subject':forms.TextInput({'style':'width:100%;'}),
            'body':forms.Textarea({'style':'width:100%;'}),
            'comment':forms.Textarea({'style':'width:100%;','rows':3})
        }

class MailGroupForm(forms.ModelForm):
    class Meta:
        model = MailGroup
        widgets = {
            'to':forms.TextInput({'style':'width:100%;'}),
            'cc':forms.TextInput({'style':'width:100%;'}),
            'ccm':forms.TextInput({'style':'width:100%;'})
        }

class MailTypeForm(forms.ModelForm):
    class Meta:
        model = MailType

class UserForm(forms.ModelForm):
    id = forms.IntegerField(required=False, initial=0, widget=widgets.HiddenInput)
    confirm_password = forms.PasswordInput()

    class Meta:
        model = User
        exclude = ('last_login','date_joined','groups','user_permissions','active')
        widgets = {
            'password':widgets.PasswordInput()
        }

class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor

