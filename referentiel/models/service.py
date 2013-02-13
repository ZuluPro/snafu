from django.db import models

class Service_Manager(models.Manager):
	def web_filter(self, GET):
		return self.get_query_set().filter(name=GET['q'])

class Service(models.Model):
	"""
	Correspond to a monitored service from a supervisor.
	"""
	name = models.CharField(max_length=128, unique=True, verbose_name='Nom')

	objects = Service_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['name']

	def __unicode__(self):
		return self.name

	def current_status(self, host) :
		from sendim.models import Alert
		if Alert.objects.filter(host__name=host, service=self).exists() :
			return Alert.objects.filter(host__name=host, service=self).order_by('-date')[0]
		else :
			return None
