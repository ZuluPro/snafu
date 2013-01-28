from django.db import models

#class Downtime_Manager(models.Manager):
#    def get_last_downtime(self, *args, **kwargs):
#        return super(Downtime_Manager, self).get_query_set().filter(*args, **kwargs)[0]

class Downtime(models.Model):
    STATUS = (
      ('STARTED','STARTED'),
      ('STOPPED','STOPPED')
    )
    
    host = models.ForeignKey('referentiel.host')
    service = models.ForeignKey('referentiel.service')
    status = models.CharField(max_length=7, choices=STATUS)
    date = models.DateTimeField()

#    objects = Downtime_Manager()
    class Meta:
        app_label = 'sendim'
        ordering = ('date',)

    def __unicode__(self):
        return self.host.name +' - '+ self.service.name
