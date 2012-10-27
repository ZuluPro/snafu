from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
 
from sendim.defs import *
from sendim.models import Alert
from sendim.forms import *
from referentiel.defs import *
from referentiel.models import Reference

@login_required
def getReferences(request) :
    """
    Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    This view is used with AJAX.
    """
    Rs = Reference.objects.all()
    if request.GET['q'] :
        Rs = (
            set( Rs.filter(host__host__icontains=request.GET['q']) ) |
            set( Rs.filter(service__service__icontains=request.GET['q']) )
        )
    return render(request, 'configuration/reference/refs/ul.html', {
        'Rs':Rs
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
def getRefForm(request,alert_id=0) :
    """
    Create a BigForm for a given alert.
    If alert_id is 0, it creates en empty form.

    This view is used with AJAX.
    """
    data = {
        'glpi_source':'Supervision',
        'apply':True
    }
    if int(alert_id) :
        A = Alert.objects.get(pk=alert_id)
        data['host'] = A.host.pk
        data['service'] = A.service.pk
        Rs = Reference.objects.filter(host=A.host,service=A.service)
        if Rs :
           for R in Rs : 
               data[R.status.status.lower()+'_criticity'] = R.mail_criticity
               data[R.status.status.lower()+'_urgency'] = R.glpi_urgency
               data[R.status.status.lower()+'_priority'] = R.glpi_priority
               data[R.status.status.lower()+'_impact'] = R.glpi_impact
               if not 'escalation_contact' in data : data['escalation_contact'] = R.escalation_contact
               if not 'tendancy' in data : data['tendancy'] = R.tendancy
               if not 'outage' in data : data['outage'] = R.outage
               if not 'explanation' in data : data['explanation'] = R.explanation
               if not 'origin' in data : data['origin'] = R.origin
               if not 'procedure' in data : data['procedure'] = R.procedure
               if not 'mail_type' in data : data['mail_type'] = R.mail_type
               if not 'mail_group' in data : data['mail_group'] = R.mail_group
               if not 'glpi_dst_group' in data : data['glpi_dst_group'] = R.glpi_dst_group
               if not 'glpi_supplier' in data : data['glpi_supplier'] = R.glpi_supplier
               if not 'glpi_category' in data : data['glpi_category'] = R.glpi_category
    
    else : data = {}
    
    Form = ReferenceBigForm(data)
    return render(request, 'configuration/reference/addref/form.html', {
         'referenceBigForm':Form
    })

