from django.forms.formsets import formset_factory
from django.conf import settings

from referentiel.models import *
from sendim.forms import *
from sendim.models import *

from common import logprint

def agregate(eventsPk, choicedEvent, message, glpi=None, mail=False, criticity='?') :
    if len(eventsPk) < 2 : return None
    for eventPk in eventsPk :
        E = Event.objects.get(pk=eventPk)
        if E.glpi : glpi = E.glpi
        if E.mail : mail= True
        if E.criticity == 'Majeur' : criticity= 'Majeur'
        if eventPk == choicedEvent: continue
        for alert in E.getAlerts() :
            alert.isPrimary = False
            alert.event = Event.objects.get(pk=choicedEvent)
            alert.save()
            logprint("Add Alert #" +str(alert.pk)+ " to Event #" +str(choicedEvent) )
        E.delete()
        logprint("Delete Event #" +eventPk, 'pink')

        E = Event.objects.get(pk=choicedEvent)
        E.message = message
        E.glpi = glpi
        E.mail = mail
        E.criticity = criticity
        E.save()
