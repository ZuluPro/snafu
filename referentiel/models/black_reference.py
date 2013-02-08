from django.db import models

class Black_reference(models.Model):
    """
    It describes alert which mustn't be treated.
    """
    host = models.ForeignKey('Host', verbose_name=u'H\xf4te')
    service = models.ForeignKey('Service')
    
    class Meta:
        app_label = 'referentiel'
        ordering = ['host','service']

    def __unicode__(self):
        return self.host.name +' - '+ self.service.name
