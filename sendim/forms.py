from referentiel.models import *
from django import forms

class TraductionBigForm(forms.Form):
	service = forms.ModelChoiceField(Service.objects.all() )
	warning = forms.CharField(max_length=300, required=True)
	critical = forms.CharField(max_length=300, required=True)
	unknown = forms.CharField(max_length=300, required=True)
	apply = forms.BooleanField()

class ReferenceBigForm(forms.Form):
    minorCriticity = MailCriticity.object.get(pk=1)
    majorCriticity = MailCriticity.object.get(pk=2)

    host = forms.ModelChoiceField(Host.objects.all().order_by('host'), required=True )
    service = forms.ModelChoiceField(Service.objects.all(), required=True  )

    escalation_contact = forms.CharField(widget=forms.HiddenInput())
    tendancy = forms.CharField(widget=forms.HiddenInput())
    outage = forms.CharField(widget=forms.HiddenInput())
    explanation = forms.CharField(widget=forms.HiddenInput())
    origin = forms.CharField(widget=forms.HiddenInput())
    procedure = forms.CharField(widget=forms.HiddenInput())

    mail_type = forms.ModelChoiceField(MailType.objects.all(), required=True  )
    mail_group = forms.ModelChoiceField(MailGroup.objects.all(), required=True  )

    warning_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    warning_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=4 )
    warning_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=2 )
    warning_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=2 )

    critical_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    critical_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=4)
    critical_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=2)
    critical_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=2 )

    unknown_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    unknown_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=4)
    unknown_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=2)
    unknown_impact = forms.ModelChoiceField(GlpiImpact.objects.all(),  initial=2)

    glpi_category = forms.ModelChoiceField(GlpiCategory.objects.all() ) 
    glpi_source = forms.CharField(initial='Supervision')
    glpi_dst_group = forms.ModelChoiceField(GlpiGroup.objects.all() ) 
    glpi_supplier = forms.ModelChoiceField(GlpiSupplier.objects.all())

