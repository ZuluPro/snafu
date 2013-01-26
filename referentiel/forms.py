from django import forms
from referentiel.models import *

class BaseReferenceForm(forms.ModelForm):
    host = forms.ModelChoiceField(Host.objects.order_by('name'), required=True)
    service = forms.ModelChoiceField(Service.objects.order_by('name'), required=True)

    mail_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1)
    glpi_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), required=True, initial=1)
    glpi_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), required=True, initial=1)
    glpi_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), required=True, initial=1)
    glpi_source = forms.CharField(initial='Supervision')

    def save(self, *args, **kwargs) :
        from sendim.models import Alert
        R = super(BaseReferenceForm, self).save(*args, **kwargs)
        for A in Alert.objects.filter(host=self.data['host'],service=self.data['service'], status=self.data['status'] ) :
            A.reference = R
            A.save()

    class Meta:
        model = Reference

class ReferenceForm(BaseReferenceForm):
    form_type = forms.CharField(initial='simple', required=False, widget=forms.widgets.HiddenInput())
    service = forms.ModelChoiceField(Service.objects.exclude(pk=1).order_by('name'), required=True)

    class Meta(BaseReferenceForm.Meta):
        pass


class HostReferenceForm(BaseReferenceForm):
    form_type = forms.CharField(initial='host', required=False, widget=forms.widgets.HiddenInput())
    service = forms.ModelChoiceField(
      Service.objects.filter(pk=1),
      initial=1,
      required=True,
      widget=forms.widgets.HiddenInput()
    )
    status = forms.ModelChoiceField(
      Status.objects.filter(name='DOWN'),
      initial=4,
      required=True,
      widget=forms.widgets.HiddenInput()
    )

    class Meta(BaseReferenceForm.Meta):
        pass

class ReferenceBigForm(BaseReferenceForm):
    form_type = forms.CharField(initial='big', required=False, widget=forms.widgets.HiddenInput())

    warning_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1)
    warning_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=1)
    warning_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=1)
    warning_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=1)

    critical_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1)
    critical_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=1)
    critical_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=1)
    critical_impact = forms.ModelChoiceField(GlpiImpact.objects.all(), initial=1)

    unknown_criticity = forms.ModelChoiceField(MailCriticity.objects.all(), required=True, initial=1)
    unknown_urgency = forms.ModelChoiceField(GlpiUrgency.objects.all(), initial=1)
    unknown_priority = forms.ModelChoiceField(GlpiPriority.objects.all(), initial=1)
    unknown_impact = forms.ModelChoiceField(GlpiImpact.objects.all(),  initial=1)

    def save(self, *args, **kwargs) :
        host = Host.objects.get(pk=self.data['host'])
        service = Service.objects.get(pk=self.data['service'])
        for status in ('warning','critical','unknown') :
            if not Reference.objects.filter(host=host,service=service,status__name=status.upper()) :
                R = Reference(
                  host = host,
                  service = service,
                  status = Status.objects.get(name=status.upper()),
  
                  escalation_contact = self.data['escalation_contact'],
                  tendancy = self.data['tendancy'],
                  outage = self.data['outage'],
                  explanation = self.data['explanation'],
                  origin = self.data['origin'],
                  procedure = self.data['procedure'],

                  mail_type = MailType.objects.get(pk=self.data['mail_type'][0]),
                  mail_group = MailGroup.objects.get(pk=self.data['mail_group'][0]),

                  glpi_category = GlpiCategory.objects.get(pk=self.data['glpi_category'][0]),
                  glpi_source = self.data['glpi_source'][0],
                  glpi_dst_group = GlpiGroup.objects.get(pk=self.data['glpi_dst_group'][0]),
                  glpi_supplier = GlpiSupplier.objects.get(pk=self.data['glpi_supplier'][0])
                )
                R.mail_criticity = MailCriticity.objects.get(pk=self.data[status+'_criticity'][0])
                R.glpi_urgency = GlpiUrgency.objects.get(pk=self.data[status+'_urgency'][0])
                R.glpi_priority = GlpiPriority.objects.get(pk=self.data[status+'_priority'][0])
                R.glpi_impact = GlpiImpact.objects.get(pk=self.data[status+'_impact'][0])
                R.save()
                from sendim.models import Alert
                for A in Alert.objects.filter(host=host,service=service, status=Status.objects.get(name=status.upper()) ) :
                    A.reference = R
                    A.save()

    def __init__(self, *args, **kwargs) :
            super(ReferenceBigForm, self).__init__(*args, **kwargs)
            del self.fields['status']
            del self.fields['mail_criticity']
            del self.fields['glpi_urgency']
            del self.fields['glpi_priority']
            del self.fields['glpi_impact']

    class Meta(BaseReferenceForm.Meta):
        pass

class BaseTranslationForm(forms.ModelForm):
    class Meta:
        model = Translation

class TranslationForm(BaseTranslationForm):
    class Meta(BaseTranslationForm.Meta):
        pass

    def save(self, *args, **kwargs) :
        from sendim.models import Alert
        T = super(TranslationForm, self).save(*args, **kwargs)
        for A in Alert.objects.filter(service=self.data['service'], translation=None) :
            A.translation = T
            A.save()

class TranslationBigForm(forms.Form):
    form_type = forms.CharField(initial='big', required=False, widget=forms.widgets.HiddenInput())
    service = forms.ModelChoiceField(Service.objects.exclude(pk=1).order_by('name'), required=True)
    warning = forms.CharField()
    critical = forms.CharField()
    unknown = forms.CharField()

    def save(self, *args, **kwargs) :
        service = Service.objects.get(pk=self.data['service'])
        for status in ('warning','critical','unknown') :
            if not Translation.objects.filter(service=service,status__name=status.upper()) :
                T = Translation(
                  service = service,
                  status = Status.objects.get(name=status.upper())
                )
                T.translation = self.data[status]
                T.save()

                from sendim.models import Alert
                for A in Alert.objects.filter(service=service, status=Status.objects.get(name=status.upper()) ) :
                    A.translation = T
                    A.save()

    class Meta(BaseReferenceForm.Meta):
        exclude = ('status','mail_criticity','glpi_urgency','glpi_priority','glpi_impact')

class BaseTranslationForm(forms.ModelForm):
    class Meta:
        model = Translation

    def save(self, *args, **kwargs) :
        from sendim.models import Alert
        T = super(TranslationForm, self).save(*args, **kwargs)

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

class GlpiGroupForm(forms.ModelForm) :
    class Meta:
        model = GlpiGroup

class GlpiSupplierForm(forms.ModelForm) :
    class Meta:
        model = GlpiSupplier

class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor

    def save(self, *args, **kwargs) :
        S = super(SupervisorForm, self).save(*args, **kwargs)
        if not 'active' in self.data.keys() :
            S.active = False
            S.save()
        return S
