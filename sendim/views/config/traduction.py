from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
 
from sendim.defs import *
from sendim.models import Alert
from sendim.forms import *
from referentiel.defs import *
from referentiel.models import Traduction

@login_required
def getTraductions(request) :
    """
    Get list of traduction filtered by service givent in GET['q']. 
    
    Includes a Paginator which split traductions into pages of 10.

    This view is used with AJAX and return traductions' tabs.
    """
    Ts = Traduction.objects.all()
    if request.GET['q'] : Ts = Ts.filter(service__name__icontains=request.GET['q'])

    Ts = Paginator(Ts, 10).page(request.GET.get('page',1))
    return render(request, 'configuration/traduction/trads/ul.html', {
        'TsPage':Ts
    })

@login_required
def traduction(request, trad_id, action="get") :
    """
    Get, add or delete a traduction.

    Delete and add :
     - Return traduction count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/traduction/trads/trad.html', {
           'T':get_object_or_404(Traduction, pk=trad_id)
        })

    elif action == "del" :
        T = get_object_or_404(Traduction, pk=trad_id)
        T.delete()
 
    elif action == "add" :
         Form = TraductionBigForm(request.POST)
         if not Form.is_valid() :
             postTraductionFormSet(request.POST)
         
    return render(request, 'configuration/traduction/tabs.html', {
        'Ts':Traduction.objects.all(),
        'AsWithoutTrad':Alert.objects.filter( Q(traduction=None), ~Q(status__name='OK'), ~Q(status__name='UP'), ~Q(status__name='DOWN') )
    })

@login_required
def getAlertWithoutTrad(request,alert_id) :
    """Get a single alert informations."""
    return render(request, 'configuration/traduction/alerts/alert.html', {
        'A':get_object_or_404(Alert, pk=alert_id)
    })

@login_required
def getAsWithoutTrad(request) :
    """
    Get alerts without traduction found by host and service.
    """
    As = Alert.objects.filter( Q(traduction=None), ~Q(status__name='OK'), ~Q(status__name='UP'), ~Q(status__name='DOWN') )
    if request.GET['q'] :
        As = list ( (
            set( As.filter(host__name__icontains=request.GET['q']) ) |
            set( As.filter(service__name__icontains=request.GET['q']) )
        ) )
    As = Paginator(As, 10).page(request.GET.get('page',1))

    return render(request, 'configuration/traduction/alerts/ul.html', {
        'AsWithoutTradPage':As
    })

@login_required
def getTradForm(request,alert_id=0) :
    """
    Create a BigForm for a given alert.
    If alert_id is 0, it creates an empty form.

    This view is used with AJAX.
    """
    data = {}
    if int(alert_id) :
        A = Alert.objects.get(pk=alert_id)
        data['service'] = A.service.pk
        Ts = Traduction.objects.filter(service=A.service)
        if Ts :
           for T in Ts :
               data[T.status.name.lower()] = T.traduction

    Form = TraductionBigForm(data)
    return render(request, 'configuration/traduction/form.html', {
         'traductionBigForm':Form
    })

