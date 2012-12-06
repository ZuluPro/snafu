from referentiel.models import *#Host

from re import match,search,sub 
from urllib2 import HTTPError


def opengraph(A, graph) :
    """Get a graph from an Alert and his url."""

    supervisor = A.host.supervisor
    opener = supervisor.getOpener()
    if supervisor.graph_type == u'N2RRD' :
        return opener.open(supervisor.index+graph).read()
    #elif supervisor.graph_type == u'RRDTool' :
    #    return opener.open(supervisor.graph+'pnp4nagios/image?host='+A.host.name+'&srv='+A.service.name.replace(' ','+')+'&view=1&source='+str(int(graph) ) ).read()

def readGraphs(host,service=None):
    """Get a list of graph with given host and service (or not)."""

    supervisor = Host.objects.get(name=host).supervisor
    opener = supervisor.getOpener()
    try :
        if supervisor.graph_type == u'N2RRD' :
            if service is None : pagehandle = opener.open(supervisor.graph+'?hostname='+host+'&service='+service.replace(' ' , '+') )
            else : pagehandle = opener.open(supervisor.graph+'?hostname='+host)
        #elif supervisor.graph_type == u'RRDTool' :
        #    if service is None : pagehandle = opener.open(supervisor.graph+'?host='+host+'&srv='+service.replace(' ' , '+')+'&view=0' )
        #    else : pagehandle = opener.open(supervisor.graph+'?host='+host)
    except HTTPError : pass
    else:
        graphList = list()
        if supervisor.graph_type == u'RRDTool' :
            for i,line in enumerate(pagehandle.readlines() ) :
                if match(r'<td.*Datasource:[^\<]*' , line ) :
                     graphList.append( ( i, sub( r".*Datasource: ([^\<]*).*" , r"\1" , line ) ) )
        elif supervisor.graph_type == u'N2RRD' :
            for line in pagehandle.readlines() :
                if search(r'n2rrd_images_cache' , line, flags=2 ) :
                     graphList.append( ( sub(r".*alt=\"([^\"]*)\".*", r"\1", line, flags=2),sub(r".*src=\"([^\"]*)\".*", r"\1", line, flags=2 ) ) )
        return graphList
