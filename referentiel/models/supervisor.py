from django.db import models
from django.utils.timezone import now

from sendim.exceptions import UnableToConnectNagios

from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener, URLError
from socket import SocketType,error,gaierror
import re
from datetime import datetime
from HTMLParser import HTMLParser
_htmlparser = HTMLParser()

from common import *

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

    name = models.CharField(max_length=200)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    index = models.CharField(max_length=300)
    status = models.CharField(max_length=300)
    history = models.CharField(max_length=300)
    graph = models.CharField(max_length=300, null=True, blank=True)
    active = models.BooleanField(default=True)

    supervisor_type = models.ForeignKey(SupervisorType, default=1)
    graph_type = models.CharField(max_length=20, choices=GRAPH_TYPE, default=None, null=True, blank=True)

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
        from sendim.models import Alert

        check = self.checkNagios()
        if check :
           raise UnableToConnectNagios(check)
    
        opener = self.getOpener()

        pagehandle = opener.open(self.history+'?host=all&archive=0&statetype=2&type=0&noflapping=on')
        problemlist = list()
        for line in pagehandle.readlines()[::-1] :
            if re.search( r"<img align='left'" , line ) :
                line = _htmlparser.unescape( line[:-1] )
    
                if re.search( 'SERVICE ALERT' , line ) :
                    problemlist.append( [ re.sub( r"^.*ALERT: ([^;]*);.*" , r"\1" , line ),
                        re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1" , line ),
                        re.sub( r".*ALERT: [^;]*;[^;]*;([^;]*);.*$" , r"\1" , line ),
                        re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;[^;]*;([^;]*)<br clear='all' />$" , r"\1" , line ),
                        re.sub( r".*>\[([^\]]*)\].*" , r"\1" , line ) ] )
    
                elif re.search( 'HOST ALERT' , line ) :
                    problemlist.append( [ re.sub( r"^.*ALERT: ([^;]*);.*" , r"\1" , line ),
                        "Host status",
                        re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1" , line ),
                        re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;([^;]*).*<br clear='all' />$" , r"\1" , line ),
                        re.sub( r".*>\[([^\]]*)\].*" , r"\1" , line ) ] )

        Es_dict = dict()
        for host,service,status,info,date in problemlist :
            
            # Try to convert date into datetime objects
            try : date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try : date = datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
                except ValueError:
                    date = now()
    
            if not Alert.objects.filter(host__name__exact=host, service__name__exact=service, date=date ).exists() :
                if not Host.objects.filter(name=host,supervisor=self).exists() :
                    Host.objects.create(name=host,supervisor=self)
                if not Service.objects.filter(name=service).exists() :
                    Service.objects.create(name=service)

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
