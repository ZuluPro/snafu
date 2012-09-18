from referentiel.models import Host, Status, Service
from django.db import models
#try : from glpidef import *
#except : pass

class Event(models.Model) :
	element = models.ForeignKey(Host)
	date = models.DateTimeField()
	criticity = models.CharField(max_length=30)
	message = models.CharField(max_length=300)
	glpi = models.IntegerField(blank=True, null=True)
	mail = models.BooleanField(default=False)

	def __unicode__(self) :
		return self.element.host+': '+self.message

	def openTicket(self) :
		pass

	def save(self, *args, **kwargs):	
		try :
			if self.ticket.glpi :
				tickets = self.ticket.glpi.replace(' ','' ).split(',')
				for t in tickets :
					addFollowed( t, "Retour du fournisseur :\n\n"+self.contenu )
		except : pass
		super(Event, self).save(*args, **kwargs)

class Alert(models.Model) :
	host = models.ForeignKey(Host)
	service = models.ForeignKey(Service)
	status = models.ForeignKey(Status)
	date = models.DateTimeField()
	info = models.CharField(max_length=300)
	event = models.ForeignKey(Event, blank=True, null=True)

	def __unicode__(self) :
		return self.host.host+':'+self.service.service

mail_types = ( (u'R\xe9seau',u'R\xe9seau'), (u'Syst\xe8me',u'Syst\xe8me'), (u'Applicatif',u'Applicatif'), (u'T\xe9l\xe9phonie',u'T\xe9l\xe9phonie') )
criticity_types = ( (u'Mineur',u'Mineur') , (u'Majeur',u'Majeur') )
glpi_urgency_types = ( (u'Basse', u'Basse'), (u'Moyenne',u'Moyenne'), (u'Haute',u'Haute'), (u'Tr\xe9s haute',u'Tr\xe9s haute') )
glpi_impact_types = ( (u'Bas', u'Bas'), (u'Moyen',u'Moyen'), (u'Haut',u'Haut'), (u'Tr\xe9s haut',u'Tr\xe9s haut') )
glpi_priority_types = ( (u'Basse', u'Basse'), (u'Moyenne',u'Moyenne'), (u'Haute',u'Haute'), (u'Tr\xe9s haute',u'Tr\xe9s haute') )
glpi_category_types = ( (u'Exploitation > R\xe9seau fixe', u'Exploitation > R\xe9seau fixe'), (u'Exploitation > Serveur',u'Exploitation > Serveur'), (u'Exploitation > R\xe9seau mobile',u'Exploitation > R\xe9seau mobile') )
glpi_source_types = ( (u'Supervision', u'Supervision') )

#class Referentiel(models.Model) :
#	host = models.CharField(max_length=30)
#	service = models.CharField(max_length=50)
#	status = models.CharField(max_length=20)
#	escalation = models.CharField(max_length=100, blank=True, null=True)
#	escalation_contact = models.CharField(max_length=100, blank=True, null=True)
#	tendancy = models.CharField(max_length=200, blank=True, null=True)
#	outage = models.CharField(max_length=100, blank=True, null=True)
#	explanation = models.CharField(max_length=200, blank=True, null=True)
#	impact = models.CharField(max_length=200, blank=True, null=True)
#	origin = models.CharField(max_length=200, blank=True, null=True)
#	procedure = models.CharField(max_length=200, blank=True, null=True)
#	mail_type = models.CharField(max_length=50, choices=mail_types)
#	mail_group = models.CharField(max_length=50, choices=mail_types)
#	mail_criticity = models.CharField(max_length=50, choices=criticity_types)
#	glpi_urgency = models.CharField(max_length=50, choices=glpi_urgency_types, blank=True, null=True)
#	glpi_impact = models.CharField(max_length=50, choices=glpi_impact_types, blank=True, null=True)
#	glpi_priority = models.CharField(max_length=50, choices=glpi_priority_types, blank=True, null=True)
#	glpi_category = models.CharField(max_length=100, choices=glpi_category_types)
#	glpi_source = models.CharField(max_length=30, choices=glpi_source_types, blank=True, null=True)
#	
#	glpi_src_user = models.CharField(max_length=50, default='PROD IT' )
#	glpi_src_group = models.CharField(max_length=50, default='Demandeurs' )
#	glpi_dst_group = models.CharField(max_length=100)
#	glpi_supplier = models.CharField(max_length=100)
#
