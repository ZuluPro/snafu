from django.db import models

class MailType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nom')

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class MailGroup(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='Nom')
    to = models.CharField(max_length=150, verbose_name=u'\xc0')
    cc = models.CharField(max_length=150, verbose_name='cc')
    ccm = models.CharField(max_length=150, verbose_name='cc majeur', help_text=u"Envoyer \xe0 ce contact en cas d'incident majeur")

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class MailCriticity(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Nom')

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name


