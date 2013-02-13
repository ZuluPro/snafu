from django.db import models

class Host_Manager(models.Manager):
	def web_filter(self, GET):
		return self.get_query_set().filter(name__icontains=GET['q'])

class Host(models.Model):
	"""
	Correspond to a monitored host from a supervisor and in GLPI.
	"""
	from referentiel.models import Supervisor
	HOST_TYPE_CHOICES = (
		(u'computer',u'computer'),
		(u'networkequipment',u'networkequipment'),
	)
	name = models.CharField(max_length=45, unique=True, verbose_name='Nom')
	glpi_id = models.IntegerField(blank=True, null=True,  default=None, verbose_name='ID GLPI')
	host_type = models.CharField(max_length=16, blank=True, choices=HOST_TYPE_CHOICES, verbose_name=u"Type d'\xe9quipement")
	supervisor = models.ForeignKey(Supervisor, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Superviseur')

	objects = Host_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['name']

	def __unicode__(self):
		return self.name

	def current_status(self) :
		return Service.objects.get(name='Host status').current_status(self.name)

	def get_graph_list(self, service):
		"""
		Shortcut which use Supervisor.get_graph_list(),
		but return [] if there's no supervisor.
		"""
		if self.supervisor :
			return self.supervisor.get_graph_list(self, service)
		else :
			return []

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
		else : return None


class Status(models.Model):
	"""
	Correspond to status of a service.
	"""
	name = models.CharField(max_length=10, unique=True, verbose_name='Nom')

	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name

