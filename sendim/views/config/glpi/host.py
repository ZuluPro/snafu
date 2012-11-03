from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from referentiel.defs import *
from referentiel.models import Host
from referentiel.forms import HostForm
from sendim.defs import get_objects_from_glpi

@login_required
def getHosts(request) :
    """
    Get list of hosts filtered by their names.
    
    Includes a Paginator which split references into pages of 10.

    This view is used with AJAX and return references' tabs.
    """
    Hs = Host.objects.all()
    if request.GET['q'] :
        Hs = Hs.filter(host__icontains=request.GET['q'])  
    Hs = Paginator(Hs, 10).page(request.GET.get('page',1))

    return render(request, 'configuration/glpi/hosts/ul.html', {
        'HsPage':Hs
    })

@login_required
def host(request, host_id, action="get") :
    """
    Get, add or delete a host.
        
    Delete :
     - Return Host count for put it in page.

    This view is used with AJAX.
    """
    if action == "get" :
        return render(request, 'configuration/glpi/hosts/host.html', {
           'H':get_object_or_404(Host, pk=host_id)
        })  
            
    elif action == "del" :
        H = get_object_or_404(Host, pk=host_id)
        H.delete()
    
    elif action == "add" :
         Form = HostForm(request.POST)
         if Form.is_valid() :
             Form.save()
         
    return render(request, 'configuration/glpi/hosts/tabs.html', {
        'Hs':Host.objects.all(),
    })

@login_required
def hostDiff(request) :
    """
    Make a diff for host between DB and GLPI.
    Return a table with : 
     - Hosts in project's DB
     - Hosts in GLPI's DB
     - Hosts without id
     - Hosts with id have changed
     - Hosts which is in project's DB but not in GLPI
     - Hosts which is in GLPI's DB but not in project's one
    """

    db_hosts = [ (H.name,H.glpi_id.__int__()) for H in Host.objects.all() if H.glpi_id ]
    glpi_hosts = [ (H.get('name','('+str(H['id'])+')'),int(H['id'])) for H in get_objects_from_glpi('host') ]
    ok_hosts = list( set(db_hosts) & set(glpi_hosts) )

    in_both = list( set([ h for h,i in db_hosts ])  & set([ h for h,i in glpi_hosts ]) )
    bad_id = list()

    no_id = [ (H.host,0) for H in Host.objects.filter(glpi_id=None) ]
    not_in_glpi = ( set(db_hosts) ^ set(glpi_hosts) ) & set(db_hosts)
    not_in_db = ( set(db_hosts) ^ set(glpi_hosts) ) & set(glpi_hosts)

    diff = {}
    diff['db'] = Host.objects.all().order_by('glpi_id')
    diff['glpi'] = glpi_hosts
    diff['ok'] = sorted(ok_hosts, key = lambda pair: pair[1])
    diff['no_id'] = no_id
    diff['bad_id'] = bad_id
    diff['not_in_glpi'] = not_in_glpi
    diff['not_in_db'] = not_in_db

    return render(request, 'configuration/glpi/hosts/diff.html', {
        'diff':diff
    })

@login_required
def getHostForm(request) :
    """
    Create a form
    This view is used with AJAX.
    """

    Form = HostForm()
    return render(request, 'configuration/glpi/hosts/form.html', {
         'HostForm':Form
    })

