from django.db import models

from referentiel.models import Host, Status, Service, Reference, Translation
from sendim.models import Event

from re import match

class Alert(models.Model) :
    host = models.ForeignKey(Host)
    service = models.ForeignKey(Service)
    status = models.ForeignKey(Status)
    date = models.DateTimeField()
    info = models.CharField(max_length=300)
    event = models.ForeignKey(Event, blank=True, null=True)
    reference = models.ForeignKey(Reference, blank=True, null=True, on_delete=models.SET_NULL)
    translation = models.ForeignKey(Translation, blank=True, null=True, on_delete=models.SET_NULL)
    isPrimary = models.BooleanField(default=False)

    class Meta:
        app_label = 'sendim'

    def __unicode__(self) :
        return self.host.name+' : '+self.service.name+' - '+ self.status.name

    def setPrimary(self):
        """Set alert as primary, set all event's alerts as not."""
        As = self.event.getAlerts().filter(isPrimary=True)
        if As :
            for A in As :
                if A is self : continue
                A.isPrimary = False
                A.save()
                #logprint("Set alert #" +str(A.pk)+ " as not primary", 'pink')
           
        self.isPrimary = True
        self.save()
        #logprint("Set primary alert for Event#"+str(self.event.pk)+" to Alert #"+str(self.pk), 'pink') 

    def find_reference(self, byHost=True, byService=True, byStatus=True):
        """
        Return a Reference which matching with the Alert.
        Searching parameters may be given with arguments.
        """ 
        Rs = Reference.objects.all()
        if byHost : Rs = Rs.filter(host=self.host)
        if byService : Rs = Rs.filter(service=self.service)
        if byStatus : Rs = Rs.filter(status=self.status)

        if Rs : return Rs[0]

    def find_translation(self, byStatus=True):
        """
        Return a Translation which matching with the Alert.
        """ 
        Ts = Translation.objects.all()
        if byStatus : Ts = Ts.filter(service=self.service, status=self.status)

        if Ts : return Ts[0]

    def linkToReference(self, force=False, byHost=True, byService=True, byStatus=True):
        """
        Search if a reference matches with the alert.
        In case, link alert to it.
        """
        if ( self.reference and force ) or not self.reference : 
            self.reference = self.find_reference(byHost, byService, byStatus)
            if self.reference : self.save()
        return self.reference

    def linkToTranslation(self, force=False, byStatus=True):
        """
        Search if a translation matches with the alert.
        In case, link alert to it.
        """
        if ( self.translation and force ) or not self.translation : 
            self.translation = self.find_translation(byStatus)
            self.save()
        return self.reference

    def link(self) :
        """
        Used for link an alert to Event. Take all case for alerts :
         - If alert is OK/UP : Link to event
         - If previous similar alert is DOWN : Link to previous alert's event
         - If previous similar alert is OK/UP : Create event and link
         - If no previous similar alert : Create Event and link
        etc...
        """
        if self.event : E = self.event

        else : 
            if match(r"^(UP|OK)$", self.status.name ) :
                if Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).exists() :
	            E = Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).order_by('-date')[0].event
		    self.event = E
	            self.save()
                else :
                    return None
            else :

                if not self.reference : R = self.find_reference()
	        if not R : mail_criticity='?'
	        else :
                    mail_criticity = R.mail_criticity
                    self.reference = R

                if not self.translation : T = self.find_translation()
                if T == None : translation=self.info
                else : translation = T.translation

                # If there's no similar alert, create Event
                if not Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).exists() :
                    E = Event(
                        element = self.host,
                        date = self.date,
                        criticity = mail_criticity,
                        message = translation
                    )
	            E.save()
                    self.event = E
                    self.isPrimary = True
                    self.save()

                else :
                    lastA = Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).order_by('-date')[0]
                    if (lastA.status in ( Status.objects.get(name='OK'), Status.objects.get(name='UP') )) or (lastA.event == None) :
                        E = Event (
                            element = self.host,
                            date = self.date,
                            criticity = mail_criticity,
                            message = translation
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

