from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
 
from sendim.defs import *
from sendim.forms import *
from referentiel.defs import *
from referentiel.models import MailType

@login_required
def getMailTypes(request) :
    """
    Get list of references filtered by host and service.
    Search GET['q'] in the 2 attributes and make a logical OR.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return references' tabs.
    """
    MTys = MailType.objects.all()
    if request.GET['q'] :
        MTys = MTys.filter(mail_group__icontains=request.GET['q'])  

    MTys = Paginator(MTys, 10).page(request.GET.get('page',1))
    return render(request, 'configuration/mail/types/ul.html', {
        'MTysPage':MTys
    })

@login_required
def mailType(request, mtype_id, action="get") :
    """
    Get or delete a reference.

    Delete :
     - Return references count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/mail/types/type.html', {
           'MTy':get_object_or_404(MailType, pk=mtype_id)
        })

    elif action == "del" :
        MTy = get_object_or_404(MailType, pk=mtype_id)
        MTy.delete()
 
    elif action == "add" :
         Form = MailTypeForm(request.POST)
         if Form.is_valid() :
             Form.save()
         
    return render(request, 'configuration/mail/types/tabs.html', {
        'MTys':MailType.objects.all()
    })

@login_required
def getMailTypeForm(request,mtype_id=0) :
    """
    Create a BigForm for a given alert.
    If alert_id is 0, it creates an empty form.

    This view is used with AJAX.
    """
    
    Form = MailTypeForm()
    return render(request, 'configuration/mail/types/form.html', {
         'MailTypeForm':Form
    })

