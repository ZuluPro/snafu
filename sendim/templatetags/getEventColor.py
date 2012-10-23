from django import template

register = template.Library()

@register.filter(name='getEventColor')
def getEventColor(E, arg=None) :
    """
    Return the class name of tr in function of alerts.
    If last alert if OK/UP, then tr will be blank.
    """

    A = E.getPrimaryAlert()
    if not A : return ''
    As = E.getAlerts().filter(host=A.host,service=A.service).exclude(pk=A.pk).order_by('-date')
    if not As : return ''

    if not As : return A.status.status.lower()+'-status'
    else :
        if As[0].status.status == 'OK' : return ''
        else : return As[0].status.status.lower()+'-status'
