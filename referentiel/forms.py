from django import forms
from referentiel.models import *

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference

class ReferenceHostStatusForm(ReferenceForm):
    service = forms.ModelChoiceField(Service.objects.get(pk=1))
    status = forms.ModelChoiceField(Status.objects.get(name='DOWN'))

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

