from django.conf import settings
from django.contrib import messages
from referentiel.models import MailType,MailGroup,Supervisor

if 'djcelery' in settings.INSTALLED_APPS :
    from djcelery.models import TaskMeta
    class CeleryMessageMiddleware(object):
        def process_request(self,request):
            if request.user.is_authenticated():
                for task in TaskMeta.objects.filter(status="SUCCESS") :
                    task_result = task.result
                    if task_result : 
                        if 'SUCCESS' in task_result :
                            messages.add_message(request, messages.SUCCESS,'<b>Lecture de '+task_result[0]+u" termin\xe9e avec succ\xe8s !</b>")
                        else :
                            messages.add_message(request, messages.ERROR,'<b>Erreur de lecture de '+task_result[0]+' : '+str(task_result[2])+'</b>')
                    task.delete()

class SnafuRequirementMiddleware(object):
    def process_request(self,request):
        if request.user.is_authenticated() and not request.is_ajax() and not request.path.startswith('/admin/'):
            messages_list = list()
            if not Supervisor.objects.exists() :
                messages_list.append('<li>Au moins 1 superviseur</li>')
            if not MailType.objects.exists() :
                messages_list.append('<li>Au moins 1 type de mail</li>')
            if not MailGroup.objects.exists() :
                messages_list.append('<li>Au moins 1 groupe de destinataire mail</li>')
            if messages_list :
                messages.add_message(request, messages.WARNING,u"<b>Attention</b>, il manque des donn\xe9es pour fonctionner :<ul>"+''.join(messages_list)+'</ul>')
