from referentiel.models import Host, Status, Service
from django.db import models

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

class Alert(models.Model) :
	host = models.ForeignKey(Host)
	service = models.ForeignKey(Service)
	status = models.ForeignKey(Status)
	date = models.DateTimeField()
	info = models.CharField(max_length=300)
	event = models.ForeignKey(Event, blank=True, null=True)

	def __unicode__(self) :
		return self.host.host+':'+self.service.service
