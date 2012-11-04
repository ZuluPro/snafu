from django.db.models import Q
from django.db import models
from common import *

from re import match

class Host(models.Model):
    HOST_TYPE_CHOICES = (
        (u'computer',u'computer'),
        (u'networkequipment',u'networkequipment'),
    )
    name = models.CharField(max_length=45, unique=True)
    glpi_id = models.IntegerField( blank=True, null=True,  default=None)
    host_type = models.CharField(max_length=16, blank=True, choices=HOST_TYPE_CHOICES)

#    def save(self, *args, **kwargs):
#        if not self.pk :
#            R = Reference(
#                host = Host.objects.get,
#                service = Service.objects.get(service='Host status'),
#                status = Status.objects.get(status='UP'),
#                escalation_contact = '', 
#                mail_type = MailType.objects.get(pk=1),
#                mail_group = MailGroup.objects.get(pk=1),
#                mail_criticity = MailCriticity.objects.get(pk=1),
#                glpi_urgency = GlpiUrgency.objects.get(pk=1),
#                glpi_priority = GlpiPriority.objects.get(pk=1),
#                glpi_impact = GlpiImpact.objects.get(pk=1),
#                glpi_category = GlpiCategory.objects.get(pk=1),
#                glpi_source = 'Supervision',
#                glpi_dst_group = GlpiGroup.objects.get(pk=1),
#                glpi_supplier = GlpiSupplier.objects.get(pk=1)
#            )
#            R.save()
#            logprint("Add Reference #"+str(R.pk)+ ' for Host' +self, 'green')            
#            self.reference = R
#        super(Host, self).save(*args, **kwargs)
#        logprint("Add automaticaly Host "+self.host, 'green')            
            
    def __unicode__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk :
            super(Service, self).save(*args, **kwargs)
            logprint('Add automaticaly service : '+self.name, 'green')

class Status(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.name

class MailType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.name

class MailGroup(models.Model):
    name = models.CharField(max_length=30, unique=True)
    to = models.CharField(max_length=150)
    cc = models.CharField(max_length=150)
    ccm = models.CharField(max_length=150)

    def __unicode__(self):
        return self.name

class MailCriticity(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

#### Objects GLPI
class GlpiUrgency(models.Model):
    name = models.CharField(max_length=128)
    glpi_id = models.IntegerField(unique=True, blank=True)

    def __unicode__(self):
        return self.name

class GlpiPriority(models.Model):
    name = models.CharField(max_length=128)
    glpi_id = models.IntegerField(unique=True, blank=True)

    def __unicode__(self):
        return self.name

class GlpiCategory(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.name

class GlpiUser(models.Model):
    name = models.CharField(max_length=128)
    glpi_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.name

class GlpiGroup(models.Model):
    name = models.CharField(max_length=128)
    glpi_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.name

class GlpiSupplier(models.Model):
    name = models.CharField(max_length=128)
    glpi_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.name

class GlpiImpact(models.Model):
    name = models.CharField(max_length=128)
    glpi_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return self.name

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

    def __unicode__(self):
        return self.host.name+' - '+self.service.name+' en '+self.status.name

class Traduction(models.Model):
    service = models.ForeignKey(Service)
    traduction = models.CharField(max_length=255)
    status = models.ForeignKey(Status)

    def __unicode__(self):
        return self.service.name+' en '+self.status.name

