from djcelery.models import TaskMeta
from django.contrib import messages

class CeleryMessageMiddleware(object):

    def process_request(self,request):
        if request.user.is_authenticated():
            for task in TaskMeta.objects.filter(status="SUCCESS") :

                task_result = task.result
                if task_result[1] == 'SUCCESS' :
                    messages.add_message(request, messages.SUCCESS,'<b>Lecture de '+task_result[0]+u" termin\xe9e avec succ\xe8s !</b>")
                else :
                    messages.add_message(request, messages.ERROR,'<b>Erreur de lecture de '+task_result[0]+' : '+str(task_result[2])+'</b>')

                task.delete()
