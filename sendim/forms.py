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

    def save(self, *args, **kwargs) :
        MT = super(MailTemplateForm, self).save(*args, **kwargs)
        if not 'chosen' in self.data.keys() :
            MT.active = False
            MT.save()
        else : MT.set_active()
        return MT

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

    def save(self, *args, **kwargs) :
        U = super(UserForm, self).save(*args, **kwargs)
        if not 'active' in self.data.keys() : U.active = False
        if not 'staff_status' in self.data.keys() : U.staff_status = False
        if not 'superuser_status' in self.data.keys() : U.superuser_status = False
        U.save()
        return U

class AuthForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.PasswordInput()

class CommandForm(forms.ModelForm):
    class Meta:
        model = Command
