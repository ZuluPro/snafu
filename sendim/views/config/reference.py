from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
 
from sendim.defs import *
from sendim.models import Alert
from sendim.forms import UserForm
from referentiel.defs import *
from referentiel.models import Reference

@login_required
def getReferences(request) :
    """
    Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return references' tabs.
    """
    Rs = Reference.objects.all()
    if request.GET['q'] :
        Rs = list( (
            set( Rs.filter(host__host__icontains=request.GET['q']) ) |
            set( Rs.filter(service__service__icontains=request.GET['q']) )
        ) )
    Rs = Paginator(Rs, 10).page(request.GET.get('page',1))
    return render(request, 'configuration/reference/refs/ul.html', {
        'RsPage':Rs
    })

@login_required
def reference(request, ref_id, action="get") :
    """
    Get or delete a reference.

    Delete :
     - Return references count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/reference/refs/ref.html', {
           'R':get_object_or_404(Reference, pk=ref_id)
        })

    elif action == "del" :
        R = get_object_or_404(Reference, pk=ref_id)
        R.delete()
 
    elif action == "add" :
         Form = ReferenceBigForm(request.POST)
         if not Form.is_valid() :
             postFormSet(request.POST, is_a_set=False)
         
    return render(request, 'configuration/reference/tabs.html', {
        'Rs':Reference.objects.all(),
        'AsWithoutRef':Alert.objects.filter( Q(reference=None), ~Q(status__status='OK'), ~Q(status__status='UP') )
    })


@login_required
def getAlertWithoutRef(request,alert_id) :
    """Get a single alert informations."""
    return render(request, 'configuration/reference/alerts/alert.html', {
        'A':get_object_or_404(Alert, pk=alert_id)
    })

@login_required
def getAsWithoutRef(request) :
    """Get references filtered by host and service."""
    As = Alert.objects.filter(reference=None)
    if request.GET['q'] :
        As = (
            set( As.filter(host__host__icontains=request.GET['q']) ) |
            set( As.filter(service__service__icontains=request.GET['q']) )
        )
    return render(request, 'configuration/reference/alerts/ul.html', {
        'AsWithoutRef':As
    })

@login_required
def getUserForm(request) :
    """
    Create a form
    This view is used with AJAX.
    """
    
    Form = UserForm
    return render(request, 'configuration/user/form.html', {
         'UserForm':Form
    })

