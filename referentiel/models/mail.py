from django.db import models

class MailCriticity(models.Model):
	name = models.CharField(max_length=20, unique=True, verbose_name='Nom')

	class Meta:
		app_label = 'referentiel'

	def __unicode__(self):
		return self.name


