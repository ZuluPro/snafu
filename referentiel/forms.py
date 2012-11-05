from django import forms
from referentiel.models import *

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference

class HostReferenceForm(ReferenceForm):
    service = forms.ModelChoiceField(
      Service.objects.filter(pk=1),
      initial=1
    )
    status = forms.ModelChoiceField(
      Status.objects.filter(name='DOWN'),
      initial=4
    )

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)

class TraductionForm(forms.Form):
    class Meta:
        model = Traduction

class HostForm(forms.ModelForm) :
    class Meta:
        model = Host

class GlpiCategoryForm(forms.ModelForm) :
    class Meta:
        model = GlpiCategory

class MailGroup(forms.ModelForm) :
    class Meta:
        model = MailGroup

