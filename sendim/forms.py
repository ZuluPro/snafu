from django.contrib.auth.models import User
from django import forms
from django.forms import widgets, formsets

from referentiel.models import *
from sendim.models import *

class TraductionBigForm(forms.Form):
    """
    A form for Traduction.
    It allow to add WARNING/CRITICAL/UNKNOWN traduction in one time.
    """

    service = forms.ModelChoiceField(Service.objects.all().order_by('name') )
    warning = forms.CharField(max_length=300, required=True)
    critical = forms.CharField(max_length=300, required=True)
    unknown = forms.CharField(max_length=300, required=True)

class ReferenceBigForm(forms.Form):
    """
    A form for Reference.
    It allow to add WARNING/CRITICAL/UNKNOWN reference in one time.
    """
    host = forms.ModelChoiceField(Host.objects.all().order_by('name'), required=True )
    service = forms.ModelChoiceField(Service.objects.all().order_by('name'), required=True)

    escalation_contact = forms.CharField(required=False)
    tendancy = forms.CharField(required=False)
    outage = forms.CharField(required=False)
    explanation = forms.CharField(required=False)
    origin = forms.CharField(required=False)
    procedure = forms.CharField(required=False)

    mail_type = forms.ModelChoiceField(MailType.objects.all(), required=True)
    mail_group = forms.ModelChoiceField(MailGroup.objects.all(), required=True)

    warning_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    warning_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=1)
    warning_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=1)
    warning_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=1)

    critical_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    critical_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=1)
    critical_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=1)
    critical_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=1)

    unknown_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1 )
    unknown_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=1)
    unknown_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=1)
    unknown_impact = forms.ModelChoiceField(GlpiImpact.objects.all(),  initial=1)

    glpi_category = forms.ModelChoiceField(GlpiCategory.objects.all() ) 
    glpi_source = forms.CharField(initial='Supervision')
    glpi_dst_group = forms.ModelChoiceField(GlpiGroup.objects.all() ) 
    glpi_supplier = forms.ModelChoiceField(GlpiSupplier.objects.all())

    def host_as_text(self):
        try : return Host.objects.get(pk=self['host'].value()).name
        except Event.DoesNotExist : return ''

    def service_as_text(self):
        try : return Service.objects.get(pk=self['service'].value()).name
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
        self.__getitem__('service')
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

    def save(self) :
        host = Host.objects.get(pk=self.data['host'])
        service = Service.objects.get(pk=self.data['service'])
    
        for status in ('WARNING','CRITICAL','UNKNOWN') :
            if not Reference.objects.filter(host=host,service=service,status__name=status) :
                R = Reference(
                    host = host,
                    service = service,
                    status = Status.objects.get(name=status),
    
                    escalation_contact = self.data['escalation_contact'],
                    tendancy = self.data['tendancy'],
                    outage = self.data['outage'],
                    explanation = self.data['explanation'],
                    origin = self.data['origin'],
                    procedure = self.data['procedure'],
    
                    mail_type = MailType.objects.get(pk=self.data['mail_type']),
                    mail_group = MailGroup.objects.get(pk=self.data['mail_group']),
    
                    glpi_category = GlpiCategory.objects.get(pk=self.data['glpi_category']),
                    glpi_source = self.data['glpi_source'],
                    glpi_dst_group = GlpiGroup.objects.get(pk=self.data['glpi_dst_group']),
                    glpi_supplier = GlpiSupplier.objects.get(pk=self.data['glpi_supplier'])
                )
                R.mail_criticity = MailCriticity.objects.get(pk=self.data[status.lower()+'_criticity'])
                R.glpi_urgency = GlpiUrgency.objects.get(pk=self.data[status.lower()+'_urgency'])
                R.glpi_priority = GlpiPriority.objects.get(pk=self.data[status.lower()+'_priority'])
                R.glpi_impact = GlpiImpact.objects.get(pk=self.data[status.lower()+'_impact'])
                R.save()

        for A in Alert.objects.filter(host=host,service=service,reference=None) :
            A.linkToReference()

class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        widgets = {
            'subject':forms.TextInput({'style' : 'width:100%;'}),
            'body':forms.Textarea({'style' : 'width:100%;'}),
            'comment':forms.Textarea({'style' : 'width:100%;','rows':3})
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
