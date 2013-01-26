from django.db import models
from referentiel.models import Host,Service

class Black_reference(models.Model):
    """
    It describes alert which mustn't be treated.
    """
    host = models.ForeignKey(Host, verbose_name=u'H\xf4te')
    service = models.ForeignKey(Service)
    
    class Meta:
        app_label = 'referentiel'
        ordering = ['host','service']
