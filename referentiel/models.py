from django.db import models
#-*- coding: utf-8 -*-
# Create your models here.
#
#CREATE TABLE referentiel (id INTEGER NOT NULL, host VARCHAR(100), service VARCHAR(100), status VARCHAR(100), escalation VARCHAR(100), escalation_contact VARCHAR(100), tendancy VARCHAR(100), outage VARCHAR(10), explanation VARCHAR(100), impact VARCHAR(100), origin VARCHAR(100), procedure VARCHAR(100), mail_type VARCHAR(100), mail_group VARCHAR(100), mail_criticity VARCHAR(100), glpi_urgency VARCHAR(100), glpi_impact VARCHAR(100), glpi_priority VARCHAR(100), glpi_category VARCHAR(100), glpi_source VARCHAR(100), glpi_src_user VARCHAR(100), glpi_src_group VARCHAR(100), glpi_dst_group VARCHAR(100), glpi_supplier VARCHAR(100), PRIMARY KEY(id));
#CREATE TABLE traductions (id INTEGER NOT NULL, service VARCHAR(100), status VARCHAR(10), traduction VARCHAR(300), PRIMARY KEY(id));

#Tables créees : 
# - host
# - statut
# - impact
# - type
# - criticite
# - groupe
# - groupe attribution
# - fournisseur
# - categorie 
# - urgence
#
# - donnees
# - traduction
# - AlertesNagios 
#
# definition de la classe host (machine) et son host_type (type de machine)


#definition de la classe "impact":
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

#definition la classe "service"
class Service(models.Model):
	service = models.CharField(max_length=128, unique=True)

	def __unicode__(self):
		return self.service

#definition de la classe "statut": critical,warning...:
class Status(models.Model):
	status = models.CharField(max_length=10, unique=True)

	def __unicode__(self):
		return self.status

#definition de la classe Type :
class MailType(models.Model):
	mail_type = models.CharField(max_length=128, unique=True)

	def __unicode__(self):
		return self.mail_type

#definition de la classe "groupe d'attribution":
class MailGroup(models.Model):
	mail_group = models.CharField(max_length=30, unique=True)
	to = models.CharField(max_length=150)
	cc = models.CharField(max_length=150)
	ccm = models.CharField(max_length=150)
	def __unicode__(self):
		return self.mail_group

#definition de la classe "criticité":
class MailCriticity(models.Model):
	mail_criticity = models.CharField(max_length=128, unique=True)

	def __unicode__(self):
		return self.mail_criticity

#### Objects GLPI
#definition la classe "urgence"
class GlpiUrgency(models.Model):
	glpi_urgency = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True, blank=True)

	def __unicode__(self):
		return self.glpi_urgency

# Definiyytion de Priorite (basse, moyenne, ... )
class GlpiPriority(models.Model):
	glpi_priority = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True, blank=True)

	def __unicode__(self):
		return self.glpi_priority

# Definition des categorie d'incident -----> populate.py
class GlpiCategory(models.Model):
	glpi_category = models.CharField(max_length=150)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_category

# Definition des users -----> populate.py
class GlpiUser(models.Model):
	glpi_user = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_user

# Definition des groups -----> populate.py
class GlpiGroup(models.Model):
	glpi_group = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_group

# Definition des fournisseurs -----> populate.py
class GlpiSupplier(models.Model):
	glpi_supplier = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_supplier

# Definition des fournisseurs -----> populate.py
class GlpiImpact(models.Model):
	glpi_impact = models.CharField(max_length=128)
	glpi_id = models.IntegerField(unique=True)

	def __unicode__(self):
		return self.glpi_impact

#definition de la classe Reference :
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
	##glpi_src_user = models.ForeignKey(GlpiUser)
	##glpi_src_group = models.ForeignKey(GlpiGroup) 
	glpi_dst_group = models.ForeignKey(GlpiGroup) ##
	glpi_supplier = models.ForeignKey(GlpiSupplier, blank=True, null=True)

	def __unicode__(self):
		return self.host.host+' - '+self.service.service+' en '+self.status.status

#definition de la classe "traduction" de l'alerte:
class Traduction(models.Model):
	service = models.ForeignKey(Service)
	traduction = models.CharField(max_length=255)
	status = models.ForeignKey(Status)

	def __unicode__(self):
		return self.service.service+' en '+self.status.status

