from django.db import models
from simple_glpi_manager import SimpleGLPI_Manager

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
