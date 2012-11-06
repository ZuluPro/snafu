from django import forms
from referentiel.models import *

class ReferenceForm(forms.Form):
	host = forms.ModelChoiceField(Host.objects.all().order_by('name') )
	service = forms.ModelChoiceField(Service.objects.all().order_by('name') )
	status = forms.ModelChoiceField(Status.objects.all() )

	escalation_contact = forms.CharField(widget=forms.HiddenInput())
	tendancy = forms.CharField(widget=forms.HiddenInput())
	outage = forms.CharField(widget=forms.HiddenInput())
	explanation = forms.CharField(widget=forms.HiddenInput())
	origin = forms.CharField(widget=forms.HiddenInput())
	procedure = forms.CharField(widget=forms.HiddenInput())

	mail_type = forms.ModelChoiceField(MailType.objects.all() )
	mail_group = forms.ModelChoiceField(MailGroup.objects.all() )
	mail_criticity = forms.ModelChoiceField(MailCriticity.objects.all() )

	glpi_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(),widget=forms.HiddenInput())
	glpi_priority = forms.ModelChoiceField(GlpiPriority.objects.all(),widget=forms.HiddenInput())
	glpi_impact = forms.ModelChoiceField(GlpiImpact.objects.all(),widget=forms.HiddenInput() )
	glpi_category = forms.ModelChoiceField(GlpiCategory.objects.all() ) ##
	glpi_source = forms.CharField(max_length=128)
	glpi_dst_group = forms.ModelChoiceField(GlpiGroup.objects.all() ) ##
	glpi_supplier = forms.ModelChoiceField(GlpiSupplier.objects.all())

class TraductionForm(forms.Form):
	service = forms.ModelChoiceField(Service.objects.all() )
	status = forms.ModelChoiceField(Status.objects.all() )
	traduction = forms.CharField(max_length=300)

class HostForm(forms.ModelForm) :
    class Meta:
        model = Host

class GlpiCategoryForm(forms.ModelForm) :
    class Meta:
        model = GlpiCategory

class MailGroup(forms.ModelForm) :
    class Meta:
        model = MailGroup

