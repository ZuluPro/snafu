from django.db import models

class Translation_Manager(models.Manager):
	def web_filter(self, GET):
		return self.get_query_set().filter(service__name=GET['q'])

class Translation(models.Model):
	"""
	Translation are used for make non technician to understand an Event.
	It will constitue the Event's message and it is facultative.
	"""
	service = models.ForeignKey('Service')
	status = models.ForeignKey('Status')
	translation = models.CharField(max_length=250, verbose_name='Traduction', help_text=u"Repr\xe9sentation simple de l'alerte.")

	objects = Translation_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['service','status']

	def __unicode__(self):
		return self.service.name+' en '+self.status.name
