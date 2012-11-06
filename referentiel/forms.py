from django import forms
from referentiel.models import *

class ReferenceForm(forms.ModelForm):
    mail_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1)
    glpi_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), required=True, initial=1)
    glpi_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), required=True, initial=1)
    glpi_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), required=True, initial=1)
    glpi_source = forms.CharField(initial='Supervision')
    
    class Meta:
        model = Reference

class HostReferenceForm(ReferenceForm):
    service = forms.ModelChoiceField(
      Service.objects.filter(pk=1),
      initial=1,
      widget=forms.widgets.HiddenInput()
    )
    status = forms.ModelChoiceField(
      Status.objects.filter(name='DOWN'),
      initial=4,
      widget=forms.widgets.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)

class TraductionForm(forms.Form):
    class Meta:
        model = Traduction

class HostForm(forms.ModelForm) :
    class Meta:
        model = Host

class MailGroupForm(forms.ModelForm) :
    class Meta:
        model = MailGroup

class GlpiCategoryForm(forms.ModelForm) :
    class Meta:
        model = GlpiCategory

class GlpiUserForm(forms.ModelForm) :
    class Meta:
        model = GlpiUser

