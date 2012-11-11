from django.forms.formsets import formset_factory

from referentiel.models import Host,Service,Reference
from sendim.forms import *

def getFormSet(E=None):
    """
    Create a sendim.forms.ReferenceBigForm set.
    
    If an Event is given as argument, Use them alerts for know how many
    forms is needed and initialize with alerts attributes.
    """
    hosts = dict()
    if E :
        for A in E.getAlerts() :
            if not A.host.name in hosts : hosts[A.host.name] = []
            if not A.service.name in hosts[A.host.name] : hosts[A.host.name].append(A.service.name)
    data = {
       'form-TOTAL_FORMS' : sum( [ len(v) for v in hosts.values() ] ),
       'form-INITIAL_FORMS': sum( [ len(v) for v in hosts.values() ] )
    }

    ReferenceBigFormSet = formset_factory(ReferenceBigForm)
    for count,(host,services) in enumerate(hosts.items()) :                                          
        for service in services :
            data['form-'+str(count)+'-host'] = Host.objects.get(name=host)
            data['form-'+str(count)+'-service'] = Service.objects.get(name=service)
            data['form-'+str(count)+'-glpi_source'] = 'Supervision'                                  
            for status in ('warning','critical','unknown') :
                data['form-'+str(count)+'-'+status+'_criticity'] = 1 
                data['form-'+str(count)+'-'+status+'_urgency'] = 3
                data['form-'+str(count)+'-'+status+'_priority'] = 3
                data['form-'+str(count)+'-'+status+'_impact'] = 4                                    
       
    return ReferenceBigFormSet(data)

def postFormSet(_POST, is_a_set=True):
    """
    This function use POST from a ReferenceBigForm for save
    WARNING/CRITICAL/UNKNOWN references.
    """
    if is_a_set :
        POST = dict()
        for k,v in _POST.items() :
            if 'form-' in k :
                POST[k[7:]] = v
    else : POST = _POST

    host = Host.objects.get(pk=POST['host'])
    service = Service.objects.get(pk=POST['service'])

    for status in ('WARNING','CRITICAL','UNKNOWN') :
        if not Reference.objects.filter(host=host,service=service,status__name=status) :
            R = Reference(
                host = host,
                service = service,
                status = Status.objects.get(name=status),

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
                glpi_supplier = GlpiSupplier.objects.get(pk=POST['glpi_supplier'])
            )
            R.mail_criticity = MailCriticity.objects.get(pk=POST[status.lower()+'_criticity'])
            R.glpi_urgency = GlpiUrgency.objects.get(pk=POST[status.lower()+'_urgency'])
            R.glpi_priority = GlpiPriority.objects.get(pk=POST[status.lower()+'_priority'])
            R.glpi_impact = GlpiImpact.objects.get(pk=POST[status.lower()+'_impact'])
            R.save()

    for A in Alert.objects.filter(host=host,service=service) :
        A.linkToReference()

    return host,service

def postTranslationFormSet(POST) :
    service = Service.objects.get(pk=POST['service'])
    for status in ('warning','critical','unknown') :
        T = Translation.objects.create(
            service = service,
            status = Status.objects.get(name=status.upper()),
            translation = POST[status]
        )

    for A in Alert.objects.filter(service=service, translation=None) :
        A.linkToTranslation()

    return service
