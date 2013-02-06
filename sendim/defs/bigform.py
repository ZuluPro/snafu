from referentiel.models import Host,Service,Reference
from referentiel.forms import HostReferenceForm, ReferenceBigForm

def getFormSet(E):
    """
    Return a forms list from a given Event.
    Used for ask References of Event's Alerts.
    """
    service_alerts = dict()
    host_alerts = list()
    if E :
        # Class missing references in a dict
        for A in E.get_alerts() :
            if A.service.name != 'Host status' :
                # Create list of service if it doesn't exists
                if not A.host.name in service_alerts :
                    service_alerts[A.host.name] = []

                if not A.service.name in service_alerts[A.host.name] and (not Reference.objects.filter(host=host,service=service).exists()) :
                    service_alerts[A.host.name].append(A.service.name)
            else :
                if (not A.host.name in host_alerts) and (not Reference.objects.filter(host=host,service='Host status').exists()) :
                    host_alerts.append(A.host.name)
                

    # Create a From for each
    form_list = list()
    ## Treat service alerts
    for host,services in service_alerts.items() :                                          
        for service in services :
            data = dict()
            data['host'] = Host.objects.get(name=host)
            data['service'] = Service.objects.get(name=service)
            data['glpi_source'] = 'Supervision'                                  
            data['form_type'] = 'big'
            for status in ('warning','critical','unknown') :
                data[status+'_criticity'] = 1 
                data[status+'_urgency'] = 3
                data[status+'_priority'] = 3
                data[status+'_impact'] = 3                                   
            form_list.append(ReferenceBigForm(data)) 
    ## Treat host alerts
    for host in host_alerts :
        data = dict()
        data['host'] = Host.objects.get(name=host)
        data['service'] = 1
        data['status'] = 4
        data['glpi_source'] = 'Supervision'                                  
        form_list.append(HostReferenceForm(data))
        data['form_type'] = 'host'                                  
       
    return form_list
