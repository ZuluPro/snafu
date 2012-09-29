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
    closed = models.BooleanField(default=False)

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
        try : return Alert.objects.filter(event=self).get(isPrimary=True)
        except Alert.DoesNotExist :
            A = self.getAlerts()[0]
            logprint("Event #"+str(self.pk)+" had no primary alert, set to the first Alert #"+str(A.pk), 'red')
            A.isPrimary = True
            A.save()
            return A

    def openTicket(self) :
    	pass

    def sendMail(self) :
    	pass

    def getReference(self) :
    	return self.getPrimaryAlert().reference

    def close(self, force=False):
        if self.closed : return None
        else :
            hosts = {}
            for A in self.getAlerts() :
                if not A.host.host in hosts : hosts[A.host.host] = []
                if not A.service.service in hosts[A.host.host] : hosts[A.host.host].append(A.service.service)
            ### Calcul de tout les service
            notOK = list()
            for host in hosts.keys() : 
                for service in hosts[host] :
                    if not self.getAlerts().filter(host__host=host,service__service=service,status=Status.objects.get(status='OK') ) :
                        notOK.append( (host,service) )
            if not notOK :
                self.closed = True
                self.save()

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
        logprint("Set primary alert for Event#"+str(self.event.pk)+": From #"+str(old_A.pk)+" to #"+str(self.pk), 'pink') 
           
        self.isPrimary = True
        self.save()

    def linkToReference(self, force=False, byHost=True, byService=True, byStatus=True):
        if ( self.reference and force ) or not self.reference : 
            self.reference = getReference(self, byHost, byService, byStatus)
            if self.reference : self.save()
        return self.reference

    def linkToTraduction(self, force=False, byStatus=True):
        if ( self.traduction and force ) or not self.traduction : 
            self.traduction = getTraduction(self, byStatus)
            self.save()
        return self.reference

    def link(self) :
        """Used for link an alert to Event. Take all case for alerts :
         -If alert is OK
         -If last alert is Ok
         -If no event exists
        etc...
        """
        if self.event : E = self.event

        else : 
            if match(r"^(UP|OK)$", self.status.status ) :
                if Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk, event=None) :
	            E = Alert.objects.filter(host=self.host,service=self.service).exclude(pk=self.pk, event=None).order_by('-pk')[0].event
		    self.event = E
	            self.save()
                else :
                    logprint("Incoherence for link Alert #"+str(self.pk)+ ", Alert has no father", 'red')
                    return None
            else :
                if not self.reference : R = getReference(self)

	        if not R : mail_criticity='?'
	        else :
                    mail_criticity = R.mail_criticity
                    self.reference = R

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
    choosen = models.BooleanField(default=False)

    def setOn(self):
        previousMT = MailTemplate.objects.get(choosen=True)
        previousMT.choosen = False
        previousMT.save()
        self.choosen = True
        self.save()

    def getOn():
        return MailTemplate.objects.get(choosen=True)
