from django.conf import settings

from sendim.models import *
from referentiel.models import *
from sendim.exceptions import UnableToConnectNagios 
from sendim.connection import getOpener, checkNagios
opener = getOpener()

from common import *
import re, time, datetime
import HTMLParser
htmlparser = HTMLParser.HTMLParser()


def opengraph(A, graph) :
    """Get a graph for an alert and a number representing the pnp view."""
    return opener.open(www+'pnp4nagios/image?host='+A.host.name+'&srv='+A.service.name.replace(' ','+')+'&view=1&source='+str(int(graph) ) ).read()

def readNagios() :
    """
    Parse Nagios history page and return a list of alert with
    host, service, status, info and date all in string format.
    
    If alert is an host alert, service will be 'Host status.
    """
    
    check = checkNagios()
    if check :
        raise UnableToConnectNagios(check)

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

        if not Alert.objects.filter(host__name__exact=host, service__name__exact=service, date=date ) :
            if not Host.objects.filter(name=host) : Host(name=host).save();
            if not Service.objects.filter(name=service) : Service(name=service).save()
            A = Alert(
                host = Host.objects.get(name=host),
                service = Service.objects.get(name=service),
                status = Status.objects.get(status=status),
                info=info,
                date=date
            )
            A.save() 
    return treatAlerts() 


def treatAlerts() :
    """
    Link all new alerts to an event.
    """
    As = list()
    for A in Alert.objects.filter(event=None) :
        if A.link() :
            As.append(A)
    return As
