from django import forms

from referentiel.models import *
from sendim.models import *

class TraductionBigForm(forms.Form):
    service = forms.ModelChoiceField(Service.objects.all() )
    warning = forms.CharField(max_length=300, required=True)
    critical = forms.CharField(max_length=300, required=True)
    unknown = forms.CharField(max_length=300, required=True)
    apply = forms.BooleanField()

class ReferenceBigForm(forms.Form):
    host = forms.ModelChoiceField(Host.objects.all().order_by('host'), required=True )
    service = forms.ModelChoiceField(Service.objects.all(), required=True  )
    apply = forms.BooleanField()

    escalation_contact = forms.CharField()
    tendancy = forms.CharField()
    outage = forms.CharField()
    explanation = forms.CharField()
    origin = forms.CharField()
    procedure = forms.CharField()

    mail_type = forms.ModelChoiceField(MailType.objects.all(), required=True  )
    mail_group = forms.ModelChoiceField(MailGroup.objects.all(), required=True  )

    warning_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    warning_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=3 )
    warning_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=3 )
    warning_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=3 )

    critical_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    critical_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=3)
    critical_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=3)
    critical_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=3 )

    unknown_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    unknown_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=3)
    unknown_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=3)
    unknown_impact = forms.ModelChoiceField(GlpiImpact.objects.all(),  initial=3)

    glpi_category = forms.ModelChoiceField(GlpiCategory.objects.all() ) 
    glpi_source = forms.CharField(initial='Supervision')
    glpi_dst_group = forms.ModelChoiceField(GlpiGroup.objects.all() ) 
    glpi_supplier = forms.ModelChoiceField(GlpiSupplier.objects.all())

    def host_as_text(self):
        try : return Host.objects.get(pk=self['host'].value()).host
        except Event.DoesNotExist : return ''

    def service_as_text(self):
        try : return Service.objects.get(pk=self['service'].value()).service
        except Event.DoesNotExist : return ''

    def warning(self):
        return [ self.__getitem__(label) for label,field in self.fields.items() if 'warning_' in label ]

    def critical(self):
        return [ self.__getitem__(label) for label,field in self.fields.items() if 'critical_' in label ]

    def unknown(self):
        return [ self.__getitem__(label) for label,field in self.fields.items() if 'unknown_' in label ]

    def all(self):
        return [ self.__getitem__(label) for label,field in self.fields.items() ]

    def alertFields(self) : 
        return [ 
        self.__getitem__('host'),
        self.__getitem__('service'),
        self.__getitem__('apply'),
        ]

    def glpiFields(self) : 
        return [ 
        self.__getitem__('glpi_category'),
        self.__getitem__('glpi_source'),
        self.__getitem__('glpi_dst_group'),
        self.__getitem__('glpi_supplier')
        ]

    def commonFields(self) : 
        return [ 
        self.__getitem__('escalation_contact'),
        self.__getitem__('tendancy'),
        self.__getitem__('outage'),
        self.__getitem__('explanation'),
        self.__getitem__('origin'),
        self.__getitem__('procedure'),
        self.__getitem__('mail_type'),
        self.__getitem__('mail_group'),
        ]

class MailTemplateForm(forms.Form):
    subject = forms.CharField(max_length=300, required=True, initial=MailTemplate.objects.get(choosen=True).subject )
    body = forms.CharField(max_length=3000, required=True, initial=MailTemplate.objects.get(choosen=True).body, widget=forms.Textarea() )
    comment = forms.CharField(max_length=3000, widget=forms.Textarea() )
    choiced = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)
        [ self.fields[key].widget.attrs.update({'style' : 'width:100%;'}) for key in self.fields.keys() ]

