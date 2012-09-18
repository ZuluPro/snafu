from django.conf import settings
from django.db.models import Q

from django.shortcuts import render

from django.template import Context, loader, RequestContext
from sendim.defs import *
from sendim.models import *
from referentiel.models import *
from referentiel.forms import *
from django.http import HttpResponse, HttpResponse

import time,datetime

def events(request, page=0) :
    page = int(page) # Le num de page peut etre passe en argument via l'URL
    contentMsg = ''
    if request.method == 'POST' :

        if 'reloadAlert_q' in request.POST :
            treatAlerts()

        if 'agregate_q' in request.POST :
            agregate(request.POST.getlist('toAgr'), request.POST['choicedEvent'], request.POST['message'] )

        if 'alertPk' in request.POST :
            alertPk = request.POST["alertPk"]
            A = Alert.objects.get(pk=alertPk)
            if 'eventPk' in request.POST :
                eventPk = request.POST["eventPk"]
                E = Event.objects.get(pk=eventPk)

        if "create_ticket_q" in request.POST :
            ticketId = createTicket( eventPk, alertPk )
            contentMsg += u"Cr\xe9ation de Du ticket #" +ticketId+ " pour l'Event #" +str(eventPk) +"<br>"

        elif "add_ref_q" in request.POST :
            default_data = { 'host':A.host.pk, 'service':A.service.pk, 'status':A.status.pk, 'mail_criticity':1,
                    'glpi_priority':4, 'glpi_urgency':4, 'glpi_impact':2, 'glpi_source':'Supervision'  }
            form = ReferenceForm(default_data, auto_id=False)
            return HttpResponse( loader.get_template('reference.form.html').render( RequestContext(request, {
                'form':form, 'alert':A, 'event':E
            } ) ) )
            

        elif "sendmail_q" in request.POST :
            sendMail( request.POST )
            contentMsg += u"Envoi du mail pour l'Event #" +str(eventPk) +"<br>"

        elif "treatment_q" in request.POST :
            if 'addRef' in request.POST :
                addRef(request.POST) # Fonction dans defs
                E.criticity = MailCriticity.objects.get(pk=request.POST['mail_criticity']).mail_criticity
                E.save()
                print "Enregistrement de "+request.POST['host']	

            if not E.glpi : ticketId = createTicket( eventPk, alertPk )
            else : ticketId = E.glpi
            # Recherche du MailGroup correspondant
            R = Reference.objects.filter(host__host__exact=A.host.host, service__service__exact=A.service.service, status__status__exact=A.status.status )[0]

            # Constitution du mail
            msg = makeMail(R,E,A,ticketId)

            # Recuperation des graphs correspondant
            graphList = readGraphs(E.element.host, A.service.service)
    
            # Envoi du formulaire d'envoi de mail
            return HttpResponse( loader.get_template('sendim.mail.html').render( RequestContext(request, {
                    'msg':msg,
                    'alert':A,
                    'event':E,
                    'graphList':graphList
            }) ))
    return HttpResponse( loader.get_template('events.html').render( RequestContext(request, {
        'events':Event.objects.order_by('-pk')[0+50*page:50+50*page],
        'alerts':Alert.objects.all(),
        'title':'Snafu - Events',
        'msg' : contentMsg,
        'page':page,
        'numPage':range(Event.objects.count()/50+1)
    }) ))

def alerts(request, page=0) :
        page = int(page) # Le num de page peut etre passe en argument via l'URL
        contentMsg = ''
	if request.method == 'POST' :
		if 'reloadAlert_q' in request.POST :
                    contentMsg += reloadAlert() # reloadAlert retourne un message en HTML
                    ## Recherche des alerts en OK n'ayant pas d'Event
                    for alert in Alert.objects.filter(  ( Q(status__status='OK')|Q(status__status='UP') ) & Q(event=None ) ) :
                        try : # Execept Si pas d'alerte trouve
                          lastEvent = Alert.objects.exclude(  Q(status__status='OK') | Q(status__status='UP') ).filter( Q(host=alert.host) & ~Q(date__gt=alert.date) & ~Q(event=None) ).order_by('-pk')[0].event
                          alert.event = lastEvent ; alert.save()
                          # contentMsg += "Ajout automatique de l'alert #" +str(alert.pk)+ u" \xe0 l'Event #" +str(lastEvent.pk) +"<br>"
                          print "Ajout automatique de l'alert #" +str(alert.pk)+ "a l'Event #" +str(lastEvent.pk)
                        except : pass # contentMsg += "Impossible de placer automatiquement l'alert #"+str(alert.pk)+u" : Pas d'Event pr\xe9c\xe9dent trouv\xe9<br>"


                elif request.POST['action'] == 'addTrad' :
                    alert = Alert.objects.get( pk=request.POST['alert_pk'] )
                    T = Traduction(
                            service = Service.objects.get(pk=request.POST['service']),
                            status = Status.objects.get(pk=request.POST['status']),
                            traduction = request.POST['traduction']
                    )
                    T.save()
                    print "Enregistrement de traduction pour "+T.service.service+" - "+T.status.status

                elif request.POST['action'] == 'addRef' :
                    alert = Alert.objects.get( pk=request.POST['alert_pk'] )
                    R = Reference(
                            host = Host.objects.get(pk=request.POST['host']),
                            service = Service.objects.get(pk=request.POST['service']),
                            status = Status.objects.get(pk=request.POST['status']),
                            escalation_contact = request.POST['escalation_contact'],
                            tendancy = request.POST['tendancy'],
                            outage = request.POST['outage'],
                            explanation = request.POST['explanation'],
                            origin = request.POST['origin'],
                            procedure = request.POST['procedure'],
                            mail_type = MailType.objects.get(pk=request.POST['mail_type']),
                            mail_group = MailGroup.objects.get(pk=request.POST['mail_group']),
                            mail_criticity = MailCriticity.objects.get(pk=request.POST['mail_criticity']),
                            glpi_urgency = GlpiUrgency.objects.get(pk=request.POST['glpi_urgency']),
                            glpi_priority = GlpiPriority.objects.get(pk=request.POST['glpi_priority']),
                            glpi_impact = GlpiImpact.objects.get(pk=request.POST['glpi_impact']),
                            glpi_category = GlpiCategory.objects.get(pk=request.POST['glpi_category']),
                            glpi_source = request.POST['glpi_source'],
                            glpi_dst_group = GlpiGroup.objects.get(pk=request.POST['glpi_dst_group']),
                            glpi_supplier = GlpiSupplier.objects.get(pk=request.POST['glpi_supplier'])
                    )
                    R.save()
                    print "Enregistrement de "+request.POST['host']	

		if 'alert_pk' in request.POST :
			alert = Alert.objects.get( pk=request.POST['alert_pk'] )

			if not re.search( r"(OK|UP)", alert.status.status ) :
				# Si pas de Ref renvoyer vers le formulaire de ref
				try :  Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service, status__status__exact=alert.status.status )[0]
				except :
                                        default_data = { 'host':alert.host.pk, 'service':alert.service.pk, 'status':alert.status.pk, 'mail_criticity':1,
                                                'glpi_priority':4, 'glpi_urgency':4, 'glpi_impact':2, 'glpi_source':'Supervision'  }
					form = ReferenceForm(default_data, auto_id=False)
					return HttpResponse( loader.get_template('reference.form.html').render( RequestContext(request, {
						'form':form, 'alert':alert
					} ) ) )
		
				# Si pas de Ref renvoyer vers le formulaire de traduction
				try :  Traduction.objects.filter( service__service__exact=alert.service.service )[0]
				except :
					default_data = { 'service':alert.service.pk, 'status':alert.status.pk }
					form = TraductionForm(default_data, auto_id=False)
					return HttpResponse( loader.get_template('traduction.form.html').render( RequestContext(request, {
						'form':form, 'alert':alert
					} ) ) )
	
			## Event
			### Recherche de la derniere alerte similaire traitee
                        try : lastAlert = Alert.objects.order_by('-date').filter( host__host__exact=alert.host.host, service__service__exact=alert.service.service ).exclude( Q(event = None) | Q(pk=alert.pk) )[0]
	                except : # Si pas d'alerte
                                E = Event(
                                        element = alert.host,
                                        date = alert.date,
                                        criticity= Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service, status__status__exact=alert.status.status )[0].mail_criticity,
                                        message = Traduction.objects.filter(service__service__exact=alert.service)[0].traduction,
                                )
                                E.save()
                                print "Creation de l'Event "+str(E.pk)
                                alert.event = E
                                alert.save()
                                # contentMsg += "Association de l'Alert #" +str(alert.pk)+ u" \xe0  l'Event #" +str(E.pk)+ "<br>"
                                print "Modification de l'alert #"+str(alert.pk)+" : Associe a l'Event #"+str(E.pk)

			else : ### Si pas d'alerte similaire traite
				### Si l'alerte est OK : Ajouter au dernier Event
				if re.search( r"(OK|UP)", alert.status.status ) :
					alert.event = Event.objects.get(pk=lastAlert.event.pk)
					alert.save()
                                        # contentMsg += "Association de l'Alert #" +str(alert.pk)+ u" \xe0  l'Event #" +str(alert.event.pk) + "<br>"
					print "Ajout de l'Alert #"+str(alert.pk)+" a l'Event #"+str(alert.event.pk)
		
				### Si la derniere traitee est en OK
				elif re.search( r"(OK|UP)", lastAlert.status.status) :
					E = Event(
						element = alert.host,
						date = alert.date,
						criticity= Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service, status__status__exact=alert.status.status )[0].mail_criticity,
						message = Traduction.objects.filter(status__status__exact=alert.status, service__service__exact=alert.service)[0].traduction,
					)
					E.save()
					print "Creation de l'Event "+str(E.pk)
					alert.event = E
					alert.save()
                                        # contentMsg += "Association de l'Alert #" +str(alert.pk)+ u" \xe0  l'Event #" +str(E.pk)+ "<br>"
					print "Modification de l'alert #"+str(alert.pk)+" : Associe a l'Event #"+str(E.pk)

				### Si 
				else :
					alert.event = Event.objects.get(pk=lastAlert.event.pk)
					alert.save()
                                        # contentMsg += "Association de l'Alert #" +str(alert.pk)+ u" \xe0  l'Event #" +str(alert.event.pk)+ "<br>"
					print "Ajout de l'Alert #"+str(alert.pk)+" a l'Event #"+str(alert.event.pk)
				
			
	return HttpResponse( loader.get_template('alerts.html').render( RequestContext(request, {
            'events':Event.objects.all(),
            'alerts':Alert.objects.order_by('-pk')[0+200*page:200+200*page],
            'title':'Snafu - Alertes',
            'msg':contentMsg,
            'page':page,
            'numPage':range(Alert.objects.count()/200+1)
	}) ))
	

def event(request, event_id) :
	return HttpResponse( loader.get_template('nagios.html').render( RequestContext(request, {
		'event':Event.objects.get(pk=event_id)
	}) ))

def createMail(request):
	E = Event.objects.get( pk=request.POST['eventPk'])
	A = Alert.objects.get(pk=request.POST['alertPk'])
	# Recherche du MailGroup correspondant
	R = Reference.objects.filter(host__host__exact=A.host.host, service__service__exact=A.service.service, status__status__exact=A.status.status )[0]

	# Constitution du mail
	msg = {} 
	msg['from'] = "Equipe d'exploitation Autolib' <it-prod@autolib.eu>"
	msg['to'] = R.mail_group.to
	if E.criticity == 'Majeur' : msg['To'] += ', '+ R.mail_group.ccm
	msg['cc'] = ' ,'.join( [ 'it-prod@autolib.eu', R.mail_group.cc] )
	msg['subject'] = '[Incident '+R.mail_type.mail_type+' Autolib\' - '+E.criticity+'] '+E.date.strftime('%d/%m/%y')+' - '+ E.message +' sur ' +E.element.host +' - GLPI '+str(E.glpi)
	with open('./mailforhost.txt' , 'r') as mailFile : msg['body'] = mailFile.read()
	
	# Recuperation des graphs correspondant
        graphList = readGraphs(E.element.host, A.service.service)

	# Envoi du formulaire d'envoi de mail
	return HttpResponse( loader.get_template('sendim.mail.html').render( RequestContext(request, {
		'msg':msg,
		'alert':A,
		'event':E, 'graphList':graphList,
                'title':'Snafu - Envoi de mail'
	}) ))

def eventHistory(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = Alert.objects.filter(date__exact=E.date)[0]
    alerts = Alert.objects.filter(host__host__exact=E.element.host, service__service__exact=A.service.service)

    return HttpResponse( loader.get_template('eventHistory.html').render( RequestContext(request, {
        'alerts':alerts[::-1],
        'event':E
    }) ))

def eventReference(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = Alert.objects.filter(event=E)[0]
    R = Reference.objects.filter(service__service__exact=A.service.service, status__status__exact=A.status.status)[0]

    return HttpResponse( loader.get_template('eventReference.html').render( RequestContext(request, {
        'reference':R,
        'event':E,
        'alert':A
    }) ))

def eventAlerts(request) :
    E = Event.objects.get( pk=request.GET['eventPk'])
    A = Alert.objects.filter(event=E)

    return HttpResponse( loader.get_template('eventAlerts.html').render( RequestContext(request, {
        'event':E,
        'alerts':A[::-1]
    }) ))

def eventsFiltered(request) :
    events = Event.objects.all()
    if request.GET['pk'] != '' : events = events.filter(pk=request.GET['pk'])
    if request.GET['element'] != '' : events = events.filter(element__host__contains=request.GET['element'])
    if request.GET['glpi'] != '' : events = events.filter(glpi__contains=request.GET['glpi'])
    if request.GET['message'] != '' : events = events.filter(message__contains=request.GET['message'])
    if request.GET['date'] != '' : pass 

    return HttpResponse( loader.get_template('events-li.html').render( RequestContext(request, {
        'events':events[::-1]
    }) ))

def eventsAgr(request) :
    events = [ Event.objects.get(pk=pk) for pk in request.GET.getlist('events[]') ]
    alerts = []
    for event in events :
        alerts.append( (event.pk, Alert.objects.filter(event=event.pk).order_by('-date') ) )

    return HttpResponse( loader.get_template('events-agr.html').render( RequestContext(request, {
        'events':events[::-1], 'alerts':alerts
    }) ))
