from django.conf import settings

from sendim.models import *
from referentiel.models import *
from sendim.exceptions import UnableToConnectNagios 

from common import *
import re, time, datetime
import HTMLParser
htmlparser = HTMLParser.HTMLParser()


def opengraph(A, graph) :
    """Get a graph for an alert and a number representing the pnp view."""
    return opener.open(www+'pnp4nagios/image?host='+A.host.name+'&srv='+A.service.name.replace(' ','+')+'&view=1&source='+str(int(graph) ) ).read()

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

def treatAlerts() :
    """
    Link all new alerts to an event.
    """
    As = list()
    for A in Alert.objects.filter(event=None) :
        if A.link() :
            As.append(A)
    return As
