from django.conf import settings

def glpi(request):
    return {
        'glpi': { 
            'index_url':settings.SENDIM['glpi-url'],
            'ticket_url':settings.SENDIM['glpi-url']+'front/ticket.form.php?id=',
            'computer_url': settings.SENDIM['glpi-url']+'front/computer.form.php?id=',
            'networkequipement_url': settings.SENDIM['glpi-url']+'front/networkequipement.form.php?id=',
            'user_url': settings.SENDIM['glpi-url']+'front/user.form.php?id=',
            'group_url': settings.SENDIM['glpi-url']+'front/group.form.php?id=',
            'itilcategory_url': settings.SENDIM['glpi-url']+'front/itilcategory.form.php?id='
        }
    }

def nagios(request):
    return {
        'nagios': { 
            'index_url':settings.SENDIM['nagios-url'],
            'host_status_url':settings.SENDIM['nagios-status']+'?host='
        }
    }
