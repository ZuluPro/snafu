from django import template
from sendim.models import Event

register = template.Library()

@register.filter(name='getEventColor')
def getEventColor(E, arg=None) :
    """
    Return the class name of tr in function of alerts.
    If last alert if OK/UP, then tr will be blank.
    """
    if isinstance(E, dict) : E = Event.objects.get(pk=E['id'])

    A = E.getPrimaryAlert()
    if not A : return ''

    As = E.get_alerts().filter(host=A.host,service=A.service).order_by('-date')
    if not As : return ''

    if not As : return A.status.name.lower()+'-status'
    else :
        if As[0].status.name == 'OK' : return ''
        elif As[0].status.name == 'DOWN': return 'critical-status'
        else : return As[0].status.name.lower()+'-status'
