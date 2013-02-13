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
	def web_filter(self, GET):
		return self.get_query_set().filter(name__icontains=GET['q'])

class GlpiCategory(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['name','glpi_id']

	def __unicode__(self):
		return self.name

class GlpiUser(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['name','glpi_id']

	def __unicode__(self):
		return self.name

class GlpiGroup(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['glpi_id']

	def __unicode__(self):
		return self.name

class GlpiSupplier(models.Model):
	name = models.CharField(max_length=150, verbose_name='Nom')
	glpi_id = models.IntegerField(unique=True, verbose_name='ID GLPI')

	objects = SimpleGLPI_Manager()
	class Meta:
		app_label = 'referentiel'
		ordering = ['glpi_id']

	def __unicode__(self):
		return self.name

