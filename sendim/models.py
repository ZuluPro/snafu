from django.db.models import Q
from django.db import models

from referentiel.models import Host, Status, Service, Reference, Traduction
from referentiel.defs import *

from common import *
from re import match


class Event(models.Model) :
    element = models.ForeignKey(Host)
    date = models.DateTimeField()
    criticity = models.CharField(max_length=30)
    message = models.CharField(max_length=300)
    glpi = models.IntegerField(blank=True, null=True)
    mail = models.BooleanField(default=False)

    def __unicode__(self) :
        return str(self.pk)+':'+self.element.host+' - '+self.message

    def getAlerts(self, isUp=True, withoutRef=False):
        As = Alert.objects.filter(event=self).order_by('-pk')
	if not isUp : As = As.exclude( Q(status__status__exact='OK') | Q(status__status__exact='UP') )
	if withoutRef : As = As.filter(reference=None)
        return As

    def getLastAlert(self, isUp=False):
        As = Alert.objects.filter(event=self).order_by('-pk')
	if not isUp : As = As.exclude( Q(status__status__exact='OK') | Q(status__status__exact='UP') )
        return As[0]

    def getPrimaryAlert(self):
        return Alert.objects.filter(event=self).get(isPrimary=True)

    def openTicket(self) :
    	pass

class Alert(models.Model) :
    host = models.ForeignKey(Host)
    service = models.ForeignKey(Service)
    status = models.ForeignKey(Status)
    date = models.DateTimeField()
    info = models.CharField(max_length=300)
    event = models.ForeignKey(Event, blank=True, null=True)
    reference = models.ForeignKey(Reference, blank=True, null=True, on_delete=models.SET_NULL)
    traduction = models.ForeignKey(Traduction, blank=True, null=True, on_delete=models.SET_NULL)
    isPrimary = models.BooleanField(default=False)


    def __unicode__(self) :
        return self.host.host+' : '+self.service.service+' - '+ self.status.status

    def setPrimary(self):
        old_A = self.event.getPrimaryAlert()
        old_A.isPrimary = False
        old_A.save()
        self.isPrimary = True
        self.save()

    def linkToReference(self, force=False, byHost=True, byService=True, byStatus=True):
        if ( self.reference and force ) or not self.reference : 
            self.reference = getReference(self, byHost, byService, byStatus)
            self.save()
        return self.reference

    def linkToTraduction(self, force=False, byStatus=True):
        if ( self.traduction and force ) or not self.traduction : 
            self.traduction = getTraduction(self, byStatus)
            self.save()
        return self.reference

    def link(self) :
        if self.event : E = self.event

        else : 
            if match(r"^(UP|OK)$", self.status.status ) :
                print Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk, event=None).order_by('-pk')
		if Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk, event=None) :
			E = Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk, event=None).order_by('-pk')[0].event
			self.event = E
			self.save()
                else :
                    logprint("Incoherence for link Alert #"+str(self.pk)+ ", Alert has no father", 'red')
                    return None
            else :
                if not self.reference : R = getReference(self)
		if R == None : mail_criticity='?'
		else : mail_criticy = R.mail_criticiry

                if not self.traduction : T = getTraduction(self)
                if T == None : traduction=self.info
		else : traduction = T.traduction

                if not Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk) :
                    E = Event (
                        element = self.host,
                        date = self.date,
                        criticity = mail_criticity,
                        message = traduction
                    )
	            E.save()
                    self.event = E
                    self.isPrimary = True
                    self.save()

                else :
                    lastA = Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk, event=None).order_by('-pk')[0]
                    if lastA.status in ( Status.objects.get(status='OK'), Status.objects.get(status='UP') ) :
                        E = Event (
                            element = self.host,
                            date = self.date,
                            criticity = mail_criticity,
                            message = traduction
                        )
                        E.save()
                        self.event = E
                        self.isPrimary = True
                        self.save()
                    else : 
                        E = lastA.event
                        self.event = E
                        self.save()
        return E

class MailTemplate(models.Model) :
    subject = models.CharField(max_length=200)
    body = models.CharField(max_length=2000)
    comment = models.CharField(max_length=300, blank=True,null=True)
    choiced = models.BooleanField(default=False)

    def setOn():
        previousMT = self.objects.get(choiced=True)
        previousMT.choiced = False
        previousMT.save()
        self.choiced = True
        self.save()

    def getOn():
        return self.objects.get(choiced=True)
