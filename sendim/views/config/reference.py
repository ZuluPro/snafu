from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from sendim.defs import *
from sendim.models import Event, Alert
from sendim.forms import *
from referentiel.defs import *
from referentiel.models import Reference

from common import logprint

@login_required
def getReferences(request) :
    """Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    This view is used with AJAX."""
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
    """Get or delete a reference.

    Delete :
     - Return user number for put it in page.

    This view is used with AJAX."""
    if action == "get" :
        return render(request, 'configuration/reference/refs/ref.html', {
           'R':get_object_or_404(Reference, pk=ref_id)
        })

    elif action == "del" :
        R = get_object_or_404(Reference, pk=ref_id)
        R.delete()
        return HttpResponse(str(Reference.objects.count())+u" r\xe9f\xe9rence(s)")


#@login_required
#def getAlertWithoutRef(request,alert_id) :
#    return render(request, 'configuration/reference/alerts/alert.html', {
#        'A':Alert.objects.get(pk=alert_id)
#    })

@login_required
def getRefForm(request,alert_id=0) :
    """Create a BigForm for a given alert.
    This view is used with AJAX."""
    A = Alert.objects.get(pk=alert_id)
    data = {
        'host':A.host.pk,
        'service':A.service.pk,
        'glpi_source':'Supervision',
        'apply':True
    }
    if request.method == 'POST' :
        POST = dict( request.POST.items() )
    	for k,v in POST.items() :
            if 'form-' in k :
                POST[k[7:]] = v
                del POST[k]
    
        for status in ('WARNING','CRITICAL','UNKNOWN') :
            if not Reference.objects.filter(host__host=host,service__service=service,status__status=status) :
                R = Reference(
                    host = host,
                    service = service,
                    status = Status.objects.get(status=status.lower()),
    
                    escalation_contact = POST['escalation_contact'],
                    tendancy = POST['tendancy'],
                    outage = POST['outage'],
                    explanation = POST['explanation'],
                    origin = POST['origin'],
                    procedure = POST['procedure'],
                
                    mail_type = MailType.objects.get(pk=POST['mail_type']),
                    mail_group = MailGroup.objects.get(pk=POST['mail_group']),
                
                    glpi_category = GlpiCategory.objects.get(pk=POST['glpi_category']),
                    glpi_source = POST['glpi_source'],
                    glpi_dst_group = GlpiGroup.objects.get(pk=POST['glpi_dst_group']),
                    glpi_supplier = GlpiSupplier.objects.get(pk=POST['glpi_supplier']),
                )
                R.mail_criticity = MailCriticity.objects.get(pk=POST[status.lower()+'_criticity'])
                R.glpi_urgency = GlpiUrgency.objects.get(pk=POST[status.lower()+'_urgency'])
                R.glpi_priority = GlpiPriority.objects.get(pk=POST[status.lower()+'_priority'])
                R.glpi_impact = GlpiImpact.objects.get(pk=POST[status.lower()+'_impact'])
                R.save()
    
            if 'apply' in request.POST :
                for A in Alert.objects.filter(host=host, service=service,reference=None) :
                    A.linkToReference()
    
    	    if 'treatment_q' in request.POST :
                E = Event.objects.get(pk=request.POST['eventPk'])
                A = E.getPrimaryAlert()
                R = getReference(A)
                A.reference = R
                A.save()
                E.criticity = R.mail_criticity.mail_criticity
                E.save()
    else :
        if alert_id :
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


