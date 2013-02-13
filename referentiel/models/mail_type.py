from django.db import models

class MailType_Manager(models.Manager):
	def web_filter(self, GET):
		"""Simple filter used by web request."""
		return self.get_query_set().filter(name__icontains=GET['q'])

class MailType(models.Model):
	"""
	Class events by type which will be show in mail.
	"""
	name = models.CharField(max_length=50, unique=True, verbose_name='Nom')

	objects = MailType_Manager()
	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name
