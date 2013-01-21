from django.db import models

class GlpiUrgency(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True, blank=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class GlpiPriority(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True, blank=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class GlpiCategory(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class GlpiUser(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True)

    class Meta:
        app_label = 'referentiel'
        ordering = ['glpi_id']

    def __unicode__(self):
        return self.name

class GlpiGroup(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True)

    class Meta:
        app_label = 'referentiel'
        ordering = ['glpi_id']

    def __unicode__(self):
        return self.name

class GlpiSupplier(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True)

    class Meta:
        app_label = 'referentiel'
        ordering = ['glpi_id']

    def __unicode__(self):
        return self.name

class GlpiImpact(models.Model):
    name = models.CharField(max_length=150)
    glpi_id = models.IntegerField(unique=True)

    class Meta:
        app_label = 'referentiel'
        ordering = ['glpi_id']

    def __unicode__(self):
        return self.name

