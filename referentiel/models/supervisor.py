from django.db import models
from django.utils.timezone import now

from sendim.exceptions import UnableToConnectNagios

from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener, URLError
from socket import error,gaierror
import re
from datetime import datetime
from HTMLParser import HTMLParser
_htmlparser = HTMLParser()

class SupervisorType(models.Model) :
    name = models.CharField(max_length=30)
    
    class Meta:
        app_label = 'referentiel'

    def __unicode__(self):
        return self.name

class Supervisor(models.Model) :
    GRAPH_TYPE = (
      ('RRDTool','RRDTool'),
      ('N2RRD','N2RRD'),
    )

    name = models.CharField(max_length=200, verbose_name='Nom')
    login = models.CharField(max_length=50, help_text=u"Nom d'utilisateur utilis\xe9 pour acc\xe9der au superviseur.")
    password = models.CharField(max_length=100, help_text=u"Nom d'utilisateur utilis\xe9 pour acc\xe9der au superviseur.")
    index = models.CharField(max_length=300, verbose_name="URL d'index", help_text=u"Index du site. (Exemple: http://www.nagios.lan).")
    status = models.CharField(max_length=300, verbose_name='URL de status', help_text=u"Index des status. (Exemple : http://www.nagios.lan/cgi-bin/status.cgi).")
    history = models.CharField(max_length=300, verbose_name="URL d'historique", help_text=u"Index de l'historique. (Exemple : http://www.nagios.lan/cgi-bin/history.cgi).")
    graph = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'URL de m\xe9trologie', help_text=u"Index de la m\xe9trologie. (Exemple : http://www.nagios.lan/cgi-bin/rrd2graph.cgi).")
    active = models.BooleanField(default=True, verbose_name='Actif')

    supervisor_type = models.ForeignKey(SupervisorType, default=1, verbose_name=u'Type de superviseur')
    graph_type = models.CharField(max_length=20, choices=GRAPH_TYPE, default=None, null=True, blank=True, verbose_name=u'Type de m\xe9trologie')

    class Meta:
        app_label = 'referentiel'
        ordering = ['name']
    
    def getOpener(self):
        """
        Return a custom urllib2 opener for logged request to supervisor.
        """
        passman = HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.index, self.login, self.password)
        authhandler = HTTPBasicAuthHandler(passman)
        opener = build_opener(authhandler)
        install_opener(opener)
        return opener

    def __unicode__(self):
        return self.name

    def checkNagios(self,timeout=2):
        """
        Make a connection test with Nagios opener.
        Return an HTML status code.
        """
        opener = self.getOpener()
        try :
            f = opener.open(self.index, timeout=timeout)
            if 'login' in f.url : nagiosStatus = True
            else : nagiosStatus = False
        except (error,gaierror,URLError,ValueError), e :
            nagiosStatus = e
        return nagiosStatus

    def parse(self) :
        """
        Parse Nagios history page and return a list of alert with
        host, service, status, info and date all in string format.
        
        If alert is an host alert, service will be 'Host status'.
        """
        from referentiel.models import Host,Service,Status
        from sendim.models import Alert, Downtime

        check = self.checkNagios()
        if check :
           raise UnableToConnectNagios(check)
    
        opener = self.getOpener()

        # Open and parse line of history
        pagehandle = opener.open(self.history+'?host=all&archive=0&statetype=2&type=0&noflapping=on')
        problemlist = list()
        for line in pagehandle.readlines()[::-1] :
            if re.search( r"<img align='left'" , line ) :
                line = _htmlparser.unescape( line[:-1] )
    
                # Try to convert date into datetime objects
                date = re.sub( r".*>\[([^\]]*)\].*", r"\1", line )
                try : date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try : date = datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
                    except ValueError:
                        date = now()

                # Create Host or Service if not exists
                if re.search(r"^.*ALERT: ([^;]*);.*",line) :
                    host = re.sub(r"^.*ALERT: ([^;]*);.*", r"\1", line)
                    service = re.sub(r".*ALERT: [^;]*;([^;]*);.*$", r"\1", line)
                    if not Host.objects.filter(name=host,supervisor=self).exists() :
                        Host.objects.create(name=host,supervisor=self)
                    if not Service.objects.filter(name=service).exists() :
                        Service.objects.create(name=service)

                # Try to find DOWNTIMES
                if 'DOWNTIME ALERT: ' in line :
                    if Downtime.objects.filter(host__name=host,service__name=service).exists() :
                        D = Downtime.objects.get(host__name=host,service__name=service)
                    else :
                        D = Downtime(
                          host=Host.objects.get(name=host),
                          service=Service.objects.get(name=service)
                        )
                    D.date = date
                    if re.search('DOWNTIME.*STARTED', line) :
                        D.status = 'STARTED'
                    elif re.search('DOWNTIME.*STOPPED', line) :
                        D.status = 'STOPPED'
                    D.save()
                    
                # Try to find Alerts
                if Downtime.objects.filter(
                  host__name=re.sub(r"^.*ALERT: ([^;]*);.*" , r"\1", line),
                  service__name=re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1", line)
                ).exists() :
                    if re.search('SERVICE ALERT', line) :
                        problemlist.append([ 
                            re.sub(r"^.*ALERT: ([^;]*);.*", r"\1", line ),
                            re.sub( r".*ALERT: [^;]*;([^;]*);.*$", r"\1", line ),
                            re.sub( r".*ALERT: [^;]*;[^;]*;([^;]*);.*$", r"\1", line ),
                            re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;[^;]*;([^;]*)<br clear='all' />$", r"\1", line ),
                            date
                        ])
        
                    elif re.search('HOST ALERT', line) :
                        problemlist.append([
                            re.sub( r"^.*ALERT: ([^;]*);.*", r"\1", line ),
                            "Host status",
                            re.sub( r".*ALERT: [^;]*;([^;]*);.*$", r"\1" , line ),
                            re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;([^;]*).*<br clear='all' />$", r"\1", line ),
                            date
                        ])

        # Walk on problemlist for create Alerts
        Es_dict = dict()
        for host,service,status,info,date in problemlist :
            
            if not Alert.objects.filter(host__name__exact=host, service__name__exact=service, date=date ).exists() :

                A = Alert(
                    host = Host.objects.get(name=host),
                    service = Service.objects.get(name=service),
                    status = Status.objects.get(name=status),
                    info=info,
                    date=date
                )
                if A.is_black_listed() : # Test if blacklisted
                    del A
                else :
                    A.link()
                    if A.event :
                        if not A.event in Es_dict : Es_dict[A.event.pk] = []
                        Es_dict[A.event.pk].append(A.pk)
        return Es_dict
