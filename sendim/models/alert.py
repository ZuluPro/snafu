from django.db import models

from referentiel.models import Host, Service, Status, Reference, Black_reference, Translation, Supervisor
from sendim.models import Event

from re import match

class Alert_Manager(models.Manager):
    def create(self, *args, **kwargs):
        """
        Create Alert and return it.
        supervisor arguments allow to link host to it.
        """
        # Try to find supervisor arg and corresponding object by name
        if Supervisor.objects.filter(name=kwargs.get('supervisor','')).exists() :
            S = Supervisor.objects.get(name=kwargs['supervisor'])
            del kwargs['supervisor']
            if not Host.objects.get(pk=kwargs['host'].pk).supervisor :
                Host.objects.filter(pk=kwargs['host'].pk).update(supervisor=S)
        return super(Alert_Manager, self).create(*args, **kwargs)

    def get_host_alert(self):
        return super(Alert_Manager, self).get_query_set().filter(service__name='Host status')

    def get_service_alert(self):
        return super(Alert_Manager, self).get_query_set().exclude(service__name='Host status')

    def get_today(self): pass

class Alert(models.Model) :
    host = models.ForeignKey('referentiel.Host')
    service = models.ForeignKey('referentiel.Service')
    status = models.ForeignKey('referentiel.Status')
    date = models.DateTimeField()
    info = models.CharField(max_length=300)
    event = models.ForeignKey('Event', blank=True, null=True)
    reference = models.ForeignKey('referentiel.Reference', blank=True, null=True, on_delete=models.SET_NULL)
    translation = models.ForeignKey('referentiel.Translation', blank=True, null=True, on_delete=models.SET_NULL)
    isPrimary = models.BooleanField(default=False)

    objects = Alert_Manager()
    class Meta:
        app_label = 'sendim'
        ordering = ('date',)

    def __init__(self, *args, **kwargs):
        # Reference temporaly Supervior in Alert object
        if 'supervisor' in kwargs :
            self.supervisor = kwargs['supervisor']
            del kwargs['supervisor']
        super(Alert,self).__init__(*args, **kwargs)

    def __unicode__(self) :
        return self.host.name+' : '+self.service.name+' - '+ self.status.name

    def save(self, *args, **kwargs):
        if 'supervisor' in dir(self) :
            self.supervisor = Supervisor.objects.get(name=self.supervisor)
            if not Host.objects.get(pk=self.host.pk).supervisor :
                Host.objects.filter(pk=self.host.pk).update(supervisor=self.supervisor)
        super(Alert, self).save(*args, **kwargs)


    def set_primary(self):
        """Set alert as primary, set all event's alerts as not."""
        self.event.getAlerts().update(isPrimary=False)
        self.isPrimary = True
        self.save()

    def is_black_listed(self):
        """
        Return True if this Alert corresponding to a Black_reference.
        """
        if Black_reference.objects.filter(host=self.host,service=self.service).exists() :
            return True
        else :
            return False

    def find_reference(self, update=True, byHost=True, byService=True, byStatus=True):
        """
        Return a Reference which matching with the Alert.
        Searching parameters may be given with arguments.
        """ 
        if not self.reference :
            Rs = Reference.objects.all()
            if byHost : Rs = Rs.filter(host=self.host)
            if byService : Rs = Rs.filter(service=self.service)
            if byStatus : Rs = Rs.filter(status=self.status)
            if Rs and update : 
                R = Rs[0]
                self.reference = R
                self.save()
                return R
        else : return self.reference

    def find_translation(self, update=True, byStatus=True):
        """
        Return a Translation which matching with the Alert.
        """ 
        if not self.translation :
            Ts = Translation.objects.all()
            if byStatus : Ts = Ts.filter(service=self.service, status=self.status)
            if Ts and update :
                T = Ts[0]
                self.translation = T
                self.save()
                return T
        else : return self.translation

    def link_to_reference(self, force=False, byHost=True, byService=True, byStatus=True):
        """
        Search if a reference matches with the alert.
        In case, link alert to it.
        """
        if ( self.reference and force ) or not self.reference : 
            self.reference = self.find_reference(byHost, byService, byStatus)
            if self.reference : self.save()
        return self.reference

    def link_to_translation(self, force=False, byStatus=True):
        """
        Search if a translation matches with the alert.
        In case, link alert to it.
        """
        if ( self.translation and force ) or not self.translation : 
            self.translation = self.find_translation(byStatus)
            self.save()
        return self.reference

    def link_to_event(self,event):
        """
        Link alert to the given event.
        If service is 'Host status', it will become primary.
        """
        self.event = event
        if self.status.name == 'DOWN' :
            self.set_primary()
        self.save()

    def create_event(self,message,mail_criticity='?'):
        """
        Create an Event corresponding to Alert.
        """
        E = Event.objects.create(
          element = self.host,
          date = self.date,
          criticity = mail_criticity,
          message = message
        )
        self.event = E
        self.set_primary()
        self.save()
        return E

    def link(self) :
        """
        Used for link an alert to Event. Take all case for alerts :
         - If alert is OK/UP : Link to event
         - If previous similar alert is DOWN : Link to previous alert's event
         - If previous similar alert is OK/UP : Create event and link
         - If no previous similar alert : Create Event and link
        etc...
        """
        if not self.event :
            # Return None if alert is OK and no corresponding alert is found
            if match(r"^(UP|OK)$", self.status.name ) :
                if Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).exists() :
	            E = Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).order_by('-date')[0].event
		    self.event = E
	            self.save()
                else :
                    return None
            else :
                # Put reference or '?'
                if self.find_reference():
                    mail_criticity = self.reference.mail_criticity
                else : mail_criticity = '?'

                # Put translation or Alert.info
                if self.find_translation():
                    translation = self.translation.translation
                else : translation = self.info

                # If there's no similar alert, create Event
                if not Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).exists() :
                    E = self.create_event(translation,mail_criticity)

                # Else find the last alert
                # If last alert is OK/UP, then create an Event
                else :
                    lastA = Alert.objects.filter(host=self.host,service=self.service).exclude(event=None).order_by('-date')[0]
                    if (lastA.status in ( Status.objects.get(name='OK'), Status.objects.get(name='UP') )) or (lastA.event == None) :
                        E = self.create_event(translation,mail_criticity)
                    else : 
                        E = lastA.event
                        self.event = E
                        self.save()
            return E
        else : return self.event

    def get_downtime_status(self):
        """Get Downtime for current Host and Service."""
        from sendim.models import Downtime
        D = Downtime.objects.get(host=self.host,service=self.service)
        return D
