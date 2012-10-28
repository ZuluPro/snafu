from django.conf import settings

from sendim.models import *
from referentiel.models import *

from common import *
import HTMLParser
import re, time, datetime

from sendim.connection import getOpener
opener = getOpener()
htmlparser = HTMLParser.HTMLParser()

def opengraph(A, graph) :
    """Get a graph for an alert and a number representing the pnp view."""
    return opener.open(www+'pnp4nagios/image?host='+A.host.host+'&srv='+A.service.service.replace(' ','+')+'&view=1&source='+str(int(graph) ) ).read()

def readNagios() :
    """
    Parse Nagios history page and return a list of alert with
    host, service, status, info and date all in string format.
    
    If alert is an host alert, service will be 'Host status.
    """
    
    pagehandle = opener.open(settings.SNAFU['nagios-history']+'?host=all&archive=0&statetype=2&type=0&noflapping=on')
    problemlist = []
    for line in pagehandle.readlines()[::-1] :
        if re.search( r"<img align='left'" , line ) :
            line = htmlparser.unescape( line[:-1] )

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
    return problemlist

def readGraphs(host,service=None):
    """
    """
    try :
        if service != None : pagehandle = opener.open(www+'pnp4nagios/graph?host='+host+'&srv='+service.replace(' ' , '+')+'&view=0' )
        else : pagehandle = opener.open(www+'pnp4nagios/graph?host='+host)
    except : pass
    else:
        graphList = list()
        for i,line in enumerate(pagehandle.readlines() ) :
            if re.match(r'<td.*Datasource:[^\<]*' , line ) :
                graphList.append( ( i, re.sub( r".*Datasource: ([^\<]*).*" , r"\1" , line ) ) )
        return graphList

def reloadAlert() :
    """
    Use alert list created by readNagios() for add alerts to database. 
    """
    logprint('Insert alerts :','pink')
    for host,service,status,info,date in readNagios() :
        # Conversion de la date nagios en object datetime
        try : date = datetime.datetime.fromtimestamp( time.mktime( time.strptime(date, "%Y-%m-%d %H:%M:%S")) )
        except ValueError:
            logprint("Nagios parsing failed on date "+date, 'yellow' )
            date = datetime.datetime.now()

        if not Alert.objects.filter(host__host__exact=host, service__service__exact=service, date=date ) :
            if not Host.objects.filter(host=host) : Host(host=host).save();
            if not Service.objects.filter(service=service) : Service(service=service).save()
            A = Alert(
                host = Host.objects.get(host=host),
                service = Service.objects.get(service=service),
                status = Status.objects.get(status=status),
                info=info,
                date=date
            )
            A.save() 
    return None


def treatAlerts() :
    """
    Link all new alerts to an event.
    """
    for A in Alert.objects.filter(event=None) :
        A.link()
    return None
