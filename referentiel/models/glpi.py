from django.db import models

class GlpiUrgency(models.Model):
	"""
	Static data imported by syncdb (initial_data).
	"""
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, blank=True, verbose_name='ID GLPI')

	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name

class GlpiPriority(models.Model):
	"""
	Static data imported by syncdb (initial_data).
	"""
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, blank=True, verbose_name='ID GLPI')

	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name

class GlpiImpact(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name

class SimpleGLPI_Manager(models.Manager):
	def __init__(self, *args, **kwargs):
		self.type = kwargs['type']
		del kwargs['type']
		super(SimpleGLPI_Manager, self).__init__(*args, **kwargs)

	def web_filter(self, GET):
		return self.get_query_set().filter(name__icontains=GET['q'])

	def glpi_list(self):
		"""List objects from GLPI."""
		from sendim.glpi_manager import GLPI_Manager
		GLPI_Manager = GLPI_Manager()
		return GLPI_Manager.list(self.type)

	def glpi_get(self, glpi_id):
		"""Get object from GLPI."""
		from sendim.glpi_manager import GLPI_Manager
		GLPI_Manager = GLPI_Manager()
		return GLPI_Manager.get(self.type, glpi_id)

class GlpiCategory(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager(type='ITILCategory')
	class Meta:
		app_label = 'referentiel'
		ordering = ['name','glpi_id']

	def __unicode__(self):
		return self.name

class GlpiUser(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager(type='user')
	class Meta:
		app_label = 'referentiel'
		ordering = ['name','glpi_id']

	def __unicode__(self):
		return self.name

class GlpiGroup(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager(type='group')
	class Meta:
		app_label = 'referentiel'
		ordering = ['glpi_id']

	def __unicode__(self):
		return self.name

class GlpiSupplier(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager(type='supplier')
	class Meta:
		app_label = 'referentiel'
		ordering = ['glpi_id']

	def __unicode__(self):
		return self.name

