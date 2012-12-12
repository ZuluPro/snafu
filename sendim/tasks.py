from django.conf import settings
if 'djcelery' in settings.INSTALLED_APPS :
    from celery.decorators import task
from sendim.exceptions import UnableToConnectNagios

@task
def reload_alerts(supervisor):
    try :
        Es = supervisor.parse()
        return (supervisor.name,'SUCCESS',Es)
    except UnableToConnectNagios, e:
        return (supervisor.name,'ERROR',e)


@task
def test(x=2):
    return x*x
