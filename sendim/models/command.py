from django.db import models
from django.utils import timezone

from commands import getstatusoutput

class Command(models.Model) :
    name = models.CharField(max_length=50)
    string = models.CharField(max_length=300)

    class Meta:
        app_label = 'sendim'

    def launch(self):
        status,out = getstatusoutput(self.string) 
        CL = CommandLog(
          date=timezone.now(),
          command=self,
          stdin=self.string,
          status=-1
        )

        if status : CL.stderr = out
        else : CL.stdout = out
        CL.status = status
        CL.save()
        return CL

    def __unicode__(self):
        return self.name
    
class CommandLog(models.Model) :
    date = models.DateTimeField()
    command = models.ForeignKey(Command, null=True)
    stdin = models.TextField(max_length=1000000)
    stdout = models.TextField(max_length=1000000, blank=True, null=True)
    stderr = models.TextField(max_length=1000000, blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        app_label = 'sendim'

    def __unicode__(self):
        return self.date.strftime('%d/%m/%Y %H:%M:%S')+' : '+str(self.command)
    
