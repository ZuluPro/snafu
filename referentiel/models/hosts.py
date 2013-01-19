from django.db import models

class Host(models.Model):
    from referentiel.models import Supervisor
    HOST_TYPE_CHOICES = (
        (u'computer',u'computer'),
        (u'networkequipment',u'networkequipment'),
    )
    name = models.CharField(max_length=45, unique=True)
    glpi_id = models.IntegerField(blank=True, null=True,  default=None)
    host_type = models.CharField(max_length=16, blank=True, choices=HOST_TYPE_CHOICES)
    supervisor = models.ForeignKey(Supervisor, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

    def current_status(self) :
        return Service.objects.get(pk=1).current_status(self.name)

class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk :
            super(Service, self).save(*args, **kwargs)
            #logprint('Add automaticaly service : '+self.name, 'green')

    def current_status(self, host) :
        from sendim.models import Alert
        if Alert.objects.filter(host__name=host, service=self).exists() :
            return Alert.objects.filter(host__name=host, service=self).order_by('-date')[0]
        else : return None


class Status(models.Model):
    name = models.CharField(max_length=10, unique=True)

    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

