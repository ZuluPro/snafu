from django.db import models

class MailType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class MailGroup(models.Model):
    name = models.CharField(max_length=30, unique=True)
    to = models.CharField(max_length=150)
    cc = models.CharField(max_length=150)
    ccm = models.CharField(max_length=150)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class MailCriticity(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name


