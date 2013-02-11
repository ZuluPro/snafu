from django.db import models

from sendim.exceptions import UnableToConnectNagios

import warnings
warnings.filterwarnings("ignore",category=UserWarning, module='urllib2')

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
    password = models.CharField(max_length=100, verbose_name='Mot de passe', help_text=u"Nom d'utilisateur utilis\xe9 pour acc\xe9der au superviseur.")
    index = models.CharField(max_length=300, verbose_name="URL d'index", help_text=u"Index du site. (Exemple: http://www.nagios.lan).")
    status = models.CharField(max_length=300, verbose_name='URL de status', help_text=u"Index des status. (Exemple : http://www.nagios.lan/cgi-bin/status.cgi).")
    history = models.CharField(max_length=300, verbose_name="URL d'historique", help_text=u"Index de l'historique. (Exemple : http://www.nagios.lan/cgi-bin/history.cgi).")
    graph = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'URL de m\xe9trologie', help_text=u"Index de la m\xe9trologie. (Exemple : http://www.nagios.lan/cgi-bin/rrd2graph.cgi).")
    active = models.BooleanField(default=False, verbose_name='Actif')
    interval = models.IntegerField(null=True, blank=True, verbose_name='Interval', help_text='Interval (en secondes) entre deux parsing')

    supervisor_type = models.ForeignKey(SupervisorType, default=1, verbose_name=u'Type de superviseur')
    graph_type = models.CharField(max_length=20, choices=GRAPH_TYPE, default=None, null=True, blank=True, verbose_name=u'Type de m\xe9trologie')

    class Meta:
        app_label = 'referentiel'
        ordering = ['name']
    
    class UnableToConnectNagios(Exception):
        """
        Unable to connect to Nagios website.
        """
        pass

    def __unicode__(self):
        return self.name

    def getOpener(self):
        """
        Return a custom urllib2 opener for logged request to supervisor.
        """
        from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener

        passman = HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.index, self.login, self.password)
        authhandler = HTTPBasicAuthHandler(passman)
        opener = build_opener(authhandler)
        install_opener(opener)
        return opener

    def checkNagios(self,timeout=2):
        """
        Make a connection test with Nagios opener.
        Return an HTML status code.
        """
        from socket import error,gaierror
        from urllib2 import URLError

        opener = self.getOpener()
        try :
            f = opener.open(self.index, timeout=timeout)
            if 'login' in f.url :
                nagiosStatus = True
            else :
                nagiosStatus = False
        except (error,gaierror,URLError,ValueError), e :
            nagiosStatus = e
        return nagiosStatus

    def parse(self) :
        """
        Parse Nagios history page and return a list of alert with
        host, service, status, info and date all in string format.
        
        If alert is an host alert, service will be 'Host status'.
        """
        from django.utils.timezone import now

        from referentiel.models import Host,Service,Status
        from sendim.models import Alert, Downtime

        from re import compile as re
        from datetime import datetime
        from HTMLParser import HTMLParser
        _htmlparser = HTMLParser()

        # Check if supervisor is foundable before everything
        check = self.checkNagios()
        if check :
           raise self.UnableToConnectNagios(check)
        
        # Make Regex for parsing
        REG_ISNOTIFICATION = re(r"<img align='left'")
        REG_ISALERT = re(r"^.*ALERT: ([^;]*);.*")
        REG_HOST = re(r"^.*ALERT: ([^;]*);.*")
        REG_SERVICE = re(r".*ALERT: [^;]*;([^;]*);.*$")
        REG_STATUS = re(r".*ALERT: [^;]*;[^;]*;([^;]*);.*$")
        REG_HOST_STATUS = re(r".*ALERT: [^;]*;([^;]*);.*$")
        REG_INFO = re(r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;[^;]*;([^;]*)<br clear='all' />$")
        REG_HOST_INFO = re(r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;([^;]*)<br clear='all' />$")
        REG_DATE = re(r".*>\[([^\]]*)\].*")
        REG_DOWNTIME_START = re(r'DOWNTIME.*STARTED')
        REG_DOWNTIME_STOP = re(r'DOWNTIME.*STOPPED')

        # Get the opener
        opener = self.getOpener()

        # Open and parse line of history
        pagehandle = opener.open(self.history+'?host=all&archive=0&statetype=2&type=0&noflapping=on')
        problemlist = list()
        for line in pagehandle.readlines()[::-1] :

            # Disqualify line
            if ('Caught SIGTERM' in line) or ("title='Program Start'" in line) or ("title='Program Restart'" in line) : continue

            # If line correspond
            elif REG_ISNOTIFICATION.search(line) :
                line = _htmlparser.unescape( line[:-1] )
    
                # Try to convert date into datetime objects
                date = REG_DATE.sub(r"\1", line)
                try : date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try : date = datetime.strptime(date, "%m-%d-%Y %H:%M:%S")
                    except ValueError:
                        date = now()

                # Create Host or Service if not exists
                if REG_ISALERT.search(line) :
                    host = REG_HOST.sub(r"\1", line)
                    service = REG_SERVICE.sub(r"\1", line)
                    if not Host.objects.filter(name=host).exists() :
                        Host.objects.create(name=host,supervisor=self)
                    if not Service.objects.filter(name=service).exists() :
                        Service.objects.create(name=service)

                # Detect if line is a Downtime notification
                if 'DOWNTIME ALERT: ' in line :
                    # Get or create
                    if Downtime.objects.filter(host__name=host,service__name=service).exists() :
                        D = Downtime.objects.get(host__name=host,service__name=service)
                    else :
                        D = Downtime(
                          host=Host.objects.get(name=host),
                          service=Service.objects.get(name=service)
                        )
                    D.date = date
                    # Detect status
                    if REG_DOWNTIME_START.search(line) :
                        D.status = 'STARTED'
                    elif REG_DOWNTIME_START.search(line) :
                        D.status = 'STOPPED'
                    D.save()
                    
                # Treat alert's notification.
                else :
                    host = REG_HOST.sub(r"\1", line)
                    service = REG_SERVICE.sub(r"\1", line)

                    # Get service's downtime status
                    if not Downtime.objects.filter(host__name=host,service__name=service).exists() :
                        D = Downtime.objects.create(
                            host=Host.objects.get(name=host),
                            service=Service.objects.get(name=service),
                            status='STOPPED',
                            date=date
                        )
                    else :
                         D = Downtime.objects.filter(
                            host__name=host,
                            service__name=service
                         )[0]

                    # For alert not on downtime
                    if D.status == 'STOPPED' :
                        if 'SERVICE ALERT' in line :
                            problemlist.append([ 
                                host,
                                REG_SERVICE.sub(r"\1", line),
                                REG_STATUS.sub(r"\1", line),
                                REG_INFO.sub(r"\1", line),
                                date
                            ])
            
                        elif 'HOST ALERT' in line :
                            problemlist.append([
                                host,
                                "Host status",
                                REG_HOST_STATUS.sub(r"\1", line),
                                REG_HOST_INFO.sub(r"\1", line),
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

    def get_graph_url(self, host=None, service=None, alert=None, prefix='image'):
        """
        Get a graph url for a couple Host & Service or an Alert.
        If supervisor has no graph return ''.
        prefix allow to use between list or graph URL.
        """
        if not self.graph :
            return ''
        # Read args
        if alert :
            host_name = alert.host.name.replace(' ','+')
            service_name = alert.service.name.replace(' ','+').replace('Host+status','_HOST_')

        else :
            host_name = host.name.replace(' ','+')
            if service :
                service_name = service.name.replace(' ','+').replace('Host+status','_HOST_')
            else :
                service_name = '_HOST_'

        # Treatment by graph type
        if self.graph_type == u'N2RRD' :
            if prefix == 'image' : 
                url = self.graph+host_name+'_'+service_name+'_Daily.png'
            else : 
                url = self.index+'/cgi-bin/rrd2graph.cgi?hostname='+host_name+'&service='+service_name

        elif self.graph_type == u'RRDTool' :
            url = self.graph+prefix+'?host='+host_name+'&srv='+service_name+'&view=0' 

        # CREATE AN EXCEPTION FOR NO GRAPH
        else :
            url = ''

        return url

    def get_graph_list(self, host, service=lambda:Service.objects.get(pk=1).name):
        """
        Get available graph for the given host and status.
        By default service is 'Host status'.
        Element of graph list is a tuple as below :
        N2RRD : (number,name,source)
        RRDTool : (name,number)
        """
        from re import match,search,sub
        from urllib2 import HTTPError

        if not self.graph :
            return []

        # Try to open graph page
        opener = self.getOpener()
        try :
            pagehandle = opener.open(self.get_graph_url(host, service, prefix='graph'))
        except (HTTPError,ValueError), e :
            return []
        else :
            # Get list of graph from page 
            graphList = list()
            if self.graph_type == u'N2RRD' :
                for line in pagehandle.readlines() :
                    if search(r'n2rrd_images_cache', line, flags=2) :
                         graphList.append((
                           len(graphList),
                           sub(r".*alt=\"([^\"]*)\".*", r"\1", line, flags=2),
                           sub(r".*src=\"([^\"]*)\".*", r"\1", line, flags=2)
                         ))
            # TEST
            elif self.graph_type == u'RRDTool' :
                for line in pagehandle.readlines() :
                    if match(r'<td.*Datasource:[^\<]*', line) :
                         graphList.append((
                           sub(r".*Datasource: ([^\<]*).*", r"\1", line),
                           len(graphList) 
                         ))
            return graphList
        return []

    def get_graph(self, alert, graph_url) :
        """Get a graph from an Alert and his url."""
        from email.mime.image import MIMEImage

        opener = self.getOpener()
        url = self.get_graph_url(alert=alert, prefix='image')

        if self.graph_type == u'N2RRD' :
            return opener.retrieve(self.index+graph_url).read()
        elif self.graph_type == u'RRDTool' :
            img =  opener.open(url+'&source='+str(int(graph_url)))

        # add header for attachement
        attachement = MIMEImage(img.read())
        attachement.add_header('Content-Disposition', 'attachment', filename='graph'+str(int(graph_url))+'.png')
        attachement.add_header('Content-Type', 'image/png', filename='graph'+str(int(graph_url))+'.png')
        return attachement
