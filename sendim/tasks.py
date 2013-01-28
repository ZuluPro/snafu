"""
Celery's tasks.
Contains periodic and backgrounded tasks.
"""

from django.conf import settings
if 'djcelery' in settings.INSTALLED_APPS :
    from celery.decorators import task
    from celery.task import PeriodicTask
    from celery.task import periodic_task
    
from referentiel.models import Supervisor
from sendim.exceptions import UnableToConnectNagios
from datetime import timedelta
from sys import stdout

def get_supervisor_task(S):
    """
    Create a periodic task for a supervisor from his interval.
    """
    # This method create dynamicaly a class object.
    @periodic_task(run_every=timedelta(seconds=S.interval))
    class supervisor_task(PeriodicTask):
        run_every = timedelta(seconds=S.interval)
        def run(self, **kwargs):
            S.parse()
    return supervisor_task

# Create supervisor's periodic tasks
for S in Supervisor.objects.filter(active=True).exclude(interval=None) :
    get_supervisor_task(S)
    stdout.write('Periodic task for ' +S.name+ ' added !\n')

@task
def reload_alerts(supervisor):
    """
    Parse a supervisor in background.
    """
    try :
        Es = supervisor.parse()
        return (supervisor.name,'SUCCESS',Es)
    except UnableToConnectNagios, e:
        return (supervisor.name,'ERROR',e)

@task
def test(x=2):
    return x*x
