from django.db import models

class Host(models.Model):
	HOST_TYPE_CHOICES = (
		(u'computer',u'computer'),
		(u'networkequipment',u'networkequipment'),
	)
	host = models.CharField(max_length=45, unique=True)
	glpi_id = models.IntegerField( blank=True, null=True,  default=None)
	host_type = models.CharField(max_length=16, blank=True, choices=HOST_TYPE_CHOICES)

	def __unicode__(self):
		return self.host

class Service(models.Model):
	service = models.CharField(max_length=128, unique=True)

	def __unicode__(self):
		return self.service

class Status(models.Model):
	status = models.CharField(max_length=10, unique=True)

	def __unicode__(self):
		return self.status

class MailType(models.Model):
	mail_type = models.CharField(max_length=128, unique=True)

	def __unicode__(self):
		return self.mail_type

class MailGroup(models.Model):
	mail_group = models.CharField(max_length=30, unique=True)
	to = models.CharField(max_length=150)
	cc = models.CharField(max_length=150)
	ccm = models.CharField(max_length=150)
	def __unicode__(self):
		return self.mail_group

class MailCriticity(models.Model):
	mail_criticity = models.CharField(max_length=128, unique=True)

	def __unicode__(self):
		return self.mail_criticity

#### Objects GLPI
class GlpiUrgency(models.Model):
	glpi_urgency = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True, blank=True)

	def __unicode__(self):
		return self.glpi_urgency

class GlpiPriority(models.Model):
	glpi_priority = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True, blank=True)

	def __unicode__(self):
		return self.glpi_priority

class GlpiCategory(models.Model):
	glpi_category = models.CharField(max_length=150)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_category

class GlpiUser(models.Model):
	glpi_user = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_user

class GlpiGroup(models.Model):
	glpi_group = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_group

class GlpiSupplier(models.Model):
	glpi_supplier = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_supplier

class GlpiImpact(models.Model):
	glpi_impact = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_impact

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
		return self.host.host+' - '+self.service.service+' en '+self.status.status

class Traduction(models.Model):
	service = models.ForeignKey(Service)
	traduction = models.CharField(max_length=255)
	status = models.ForeignKey(Status)

	def __unicode__(self):
		return self.service.service+' en '+self.status.status

