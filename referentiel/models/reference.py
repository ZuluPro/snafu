from django.db import models
from referentiel.models import *

class Reference(models.Model):
    host = models.ForeignKey(Host)
    service = models.ForeignKey(Service)
    status = models.ForeignKey(Status)

    escalation_contact = models.CharField(max_length=100, blank=True, null=True)
    tendancy = models.CharField(max_length=200, blank=True, null=True)
    outage = models.CharField(max_length=200, blank=True, null=True)
    explanation = models.CharField(max_length=200, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    procedure = models.CharField(max_length=255, blank=True, null=True)

    mail_type = models.ForeignKey(MailType)
    mail_group = models.ForeignKey(MailGroup)
    mail_criticity = models.ForeignKey(MailCriticity)

    glpi_urgency = models.ForeignKey(GlpiUrgency, blank=True, null=True )
    glpi_priority = models.ForeignKey(GlpiPriority, blank=True)
    glpi_impact = models.ForeignKey(GlpiImpact)
    glpi_category = models.ForeignKey(GlpiCategory) ##
    glpi_source = models.CharField(max_length=128, blank=True)
    glpi_dst_group = models.ForeignKey(GlpiGroup) ##
    glpi_supplier = models.ForeignKey(GlpiSupplier, blank=True, null=True)

    class Meta:
        app_label = 'referentiel'
        ordering = ['host','service','status']

    def __unicode__(self):
        return self.host.name+' - '+self.service.name+' en '+self.status.name

class Translation(models.Model):
    service = models.ForeignKey(Service)
    translation = models.CharField(max_length=250)
    status = models.ForeignKey(Status)

    class Meta:
        app_label = 'referentiel'
        ordering = ['service','status']

    def __unicode__(self):
        return self.service.name+' en '+self.status.name

