from django.db import models

class Black_reference_Manager(models.Manager):
	def web_filter(self, GET):
		qset = self.get_query_set()
		return list((
		  set(qset.filter(host__name__icontains=GET['q'])) |
		  set(qset.filter(service__name__icontains=GET['q']))
		))

class Black_reference(models.Model):
	"""
	It describes alert which mustn't be treated.
	"""
	host = models.ForeignKey('Host', verbose_name=u'H\xf4te')
	service = models.ForeignKey('Service')
	
	objects = Black_reference_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['host','service']

	def __unicode__(self):
		return self.host.name +' - '+ self.service.name
