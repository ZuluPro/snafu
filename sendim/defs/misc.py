from sendim.models import Event

def aggregate(eventsPk, choicedEvent, message, glpi=None, mail=False, criticity='?') :
    """
    Aggregate several events in one.
    """
    if len(eventsPk) < 2 : return None
    for eventPk in eventsPk :
        E = Event.objects.get(pk=eventPk)
        if E.glpi : glpi = E.glpi
        if E.mail : mail= True
        if E.criticity == 'Majeur' : criticity= 'Majeur'
        if eventPk == choicedEvent: continue
        for alert in E.get_alerts() :
            alert.isPrimary = False
            alert.event = Event.objects.get(pk=choicedEvent)
            alert.save()
        E.delete()

    E = Event.objects.get(pk=choicedEvent)
    E.message = message
    E.glpi = glpi
    E.mail = mail
    E.criticity = criticity
    E.save()
    return E
