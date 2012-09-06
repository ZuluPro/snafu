from django.db.models import Q
from django.db import models

from referentiel.models import Host, Status, Service
from referentiel.defs import *

class Event(models.Model) :
    element = models.ForeignKey(Host)
    date = models.DateTimeField()
    criticity = models.CharField(max_length=30)
    message = models.CharField(max_length=300)
    glpi = models.IntegerField(blank=True, null=True)
    mail = models.BooleanField(default=False)

    def __unicode__(self) :
        return self.element.host+': '+self.message

    def getLastAlert(self, isUp=False):
        return Alert.objects.filter(
            Q(event__pk=self.pk),
            Q(status__status__exact='OK') | Q(status__status__exact='UP')
        ).order_by('-pk')[0]

    def openTicket(self) :
    	pass

class Alert(models.Model) :
    host = models.ForeignKey(Host)
    service = models.ForeignKey(Service)
    status = models.ForeignKey(Status)
    date = models.DateTimeField()
    info = models.CharField(max_length=300)
    event = models.ForeignKey(Event, blank=True, null=True)

    def __unicode__(self) :
        return self.host.host+':'+self.service.service

    def link(self) :
        if self.event : E = self.event ; print 123
        else : 
            R = getReference(self)
            T = getTraduction(self)
            if not Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk) :

                E = Event (
                    element = self.host,
                    date = self.date,
                    criticity = R.mail_criticity,
                    message = T.traduction
                )
	        E.save()
                self.event = E
                self.save()
        return E
