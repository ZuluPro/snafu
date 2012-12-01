from django import template

register = template.Library()

@register.filter(name='getEscalation')
def getEscalation(E, arg=None) :
    """Return escalation of event's primary alert."""
    A = E.getPrimaryAlert() 
    R = A.reference

    if R : return R.escalation_contact
    else : return None
