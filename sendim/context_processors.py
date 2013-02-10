from django.conf import settings

from sendim.models import Alert

def sendim_context(request):
    return {
        'alert': {
            'without_ref':Alert.objects.filter(reference=None).count()
        },
        'glpi': { 
            'index_url':settings.SNAFU['glpi-url'],
            'ticket_url':settings.SNAFU['glpi-url']+'front/ticket.form.php?id=',
            'computer_url': settings.SNAFU['glpi-url']+'front/computer.form.php?id=',
            'networkequipement_url': settings.SNAFU['glpi-url']+'front/networkequipement.form.php?id=',
            'user_url': settings.SNAFU['glpi-url']+'front/user.form.php?id=',
            'group_url': settings.SNAFU['glpi-url']+'front/group.form.php?id=',
            'itilcategory_url': settings.SNAFU['glpi-url']+'front/itilcategory.form.php?id=',
            1:1#'connection':checkGlpi()
	},
        'smtp': {
            1:1#'connection':checkSmtp()
        }
    }
