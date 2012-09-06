from django.views.decorators.csrf import csrf_exempt 
from django.http import HttpResponse

from sendim.models import Alert
from sendim.models import Host,Service,Status

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from datetime import datetime

dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None) # Python 2.5

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
                response.write("You need to invoke it using an XML-RPC Client!<br>")
                response.write("The following methods are available:<ul>")
                methods = dispatcher.system_listMethods()

                for method in methods:
                        # right now, my version of SimpleXMLRPCDispatcher always
                        # returns "signatures not supported"... :(
                        # but, in an ideal world it will tell users what args are expected
                        sig = dispatcher.system_methodSignature(method)

                        # this just reads your docblock, so fill it in!
                        help =  dispatcher.system_methodHelp(method)

                        response.write("<li><b>%s</b>: [%s] %s" % (method, sig, help))

                response.write("</ul>")
                response.write('<a href="http://www.djangoproject.com/"> <img src="http://media.djangoproject.com/img/badges/djangomade124x25_grey.gif" border="0" alt="Made with Django." title="Made with Django."></a>')

        response['Content-length'] = str(len(response.content))
        return response

def test(test="Ok"):
    return test

def pushAlert(host,service,status,info,date=datetime.now()):
    if type(date) == type('') : date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S' )
    A = Alert(
        host = Host.objects.get(host=host),
        service = Service.objects.get(service=service),
        status = Status.objects.get(status=status),
        info = info,
        date = date
    )
    A.save()
    return A

dispatcher.register_function(test, 'test')
dispatcher.register_function(pushAlert, 'pushAlert')
