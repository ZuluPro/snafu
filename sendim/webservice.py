from django.views.decorators.csrf import csrf_exempt 
from django.http import HttpResponse

from sendim.models import Alert
from sendim.models import Host,Service,Status

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

def pushAlert(host,service,status,info,date=None):
    """Create a new alert."""
    if not date : date = datetime.now()
    elif type(date) == type('') : date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S' )
    
    A = Alert(
        host = Host.objects.get(name=host),
        service = Service.objects.get(service=service),
        status = Status.objects.get(status=status),
        info = info,
        date = date
    )
    A.save()
    A.link()
    return A

dispatcher.register_function(test, 'test')
dispatcher.register_function(pushAlert, 'pushAlert')
