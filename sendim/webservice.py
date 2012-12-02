from django.views.decorators.csrf import csrf_exempt 
from django.http import HttpResponse
from django.utils import timezone

from sendim.models import Alert
from referentiel.models import Host,Service,Status,Supervisor

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from datetime import datetime

dispatcher = SimpleXMLRPCDispatcher(allow_none=True, encoding=None)

@csrf_exempt 
def webservice(request):
    """
    the actual handler:
    if you setup your urls.py properly, all calls to the xml-rpc service
    should be routed through here.
    If post data is defined, it assumes it's XML-RPC and tries to process as such
    Empty post assumes you're viewing from a browser and tells you about the service.
    """

    if len(request.POST):
        response = HttpResponse(mimetype="application/xml")
        response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
    else:
        response = HttpResponse()
        response.write("<b>This is an XML-RPC Service.</b><br>")

    response['Content-length'] = str(len(response.content))
    return response

def test():
    """A simple test for webservice."""
    return 0

def pushAlert(host,service,status,info,supervisor,date=None):
    """Create a new alert."""
    try : supervisor = Supervisor.objects.get(name=supervisor)
    except Supervisor.DoesNotExist : supervisor = None

    if not date : date = timezone.now()
    elif type(date) == type('') :
        try: date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S' )
        except ValueError:
            try : date = datetime.strptime(date, '%m-%d-%Y %H:%M:%S' )
            except ValueError: date = timezone.now()
 
    
    if not Alert.objects.filter(host__name__exact=host, service__name__exact=service, date=date ).exists() :
        if not Host.objects.filter(name=host):
            Host.objects.create(name=host,supervisor=supervisor)
        if not Service.objects.filter(name=service):
            Service.objects.create(name=service)

        A = Alert.objects.create(
            host = Host.objects.get(name=host),
            service = Service.objects.get(name=service),
            status = Status.objects.get(name=status),
            info = info,
            date = date
        )
        A.link()

dispatcher.register_function(test, 'test')
dispatcher.register_function(pushAlert, 'pushAlert')
