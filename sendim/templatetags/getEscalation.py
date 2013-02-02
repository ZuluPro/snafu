from django import template
from sendim.models import Event

register = template.Library()

@register.filter(name='getEscalation')
def getEscalation(E, arg=None) :
    """Return escalation of event's primary alert."""
    if isinstance(E, dict) : E = Event.objects.get(pk=E['id'])

    A = E.get_primary_alert() 
    if A is None : return None

    R = A.reference
    if R : return R.escalation_contact
    else : return None
