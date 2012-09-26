from django.conf import settings

from sendim.models import Alert

def glpi(request):
    return {
        'glpi': { 
            'index_url':settings.SNAFU['glpi-url'],
            'ticket_url':settings.SNAFU['glpi-url']+'front/ticket.form.php?id=',
            'computer_url': settings.SNAFU['glpi-url']+'front/computer.form.php?id=',
            'networkequipement_url': settings.SNAFU['glpi-url']+'front/networkequipement.form.php?id=',
            'user_url': settings.SNAFU['glpi-url']+'front/user.form.php?id=',
            'group_url': settings.SNAFU['glpi-url']+'front/group.form.php?id=',
            'itilcategory_url': settings.SNAFU['glpi-url']+'front/itilcategory.form.php?id='
        }
    }

def nagios(request):
    print 123
    return {
        'nagios': { 
            'index_url':settings.SNAFU['nagios-url'],
            'host_status_url':settings.SNAFU['nagios-status']+'?host='
        },
        'ref': {
            'ref':Alert.objects.filter(reference=None).count()
        }
    }

def refe(request):
    return {
        'ref': { 
        }
    }
