from django.template import Context, loader
from django.http import HttpResponse
from referentiel.models import *


def reference(request):
    A = Alert.objects.get(pk=request.POST['alertPk'])
    E = Event.objects.get(pk=request.POST['eventPk'])

    T = Traduction.objects.get(status=A.status, service__name__exact=alert.service)

    return HttpResponse( loader.get_template('nagios.html').render( RequestContext(request, {
        'dadate':datetime.datetime.now() ,
        }) ))
