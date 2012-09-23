from django.conf import settings

from sendim.models import *
from referentiel.models import *

from common import $
import urllib2, HTMLParser
import re, time, datetime

www = settings.SENDIM['nagios-url']
username = settings.SENDIM['nagios-login']
password = settings.SENDIM['nagios-password']
htmlparser = HTMLParser.HTMLParser()

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, www, username, password)
authhandler = urllib2.HTTPBasicAuthHandler(passman)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener(opener)

def opengraph(alert, graph) :
    return opener.open(www+'pnp4nagios/image?host='+alert.host.host+'&srv='+alert.service.service.replace(' ','+')+'&view=1&source='+str(int(graph) ) ).read()

def readNagios() :
        pagehandle = opener.open(settings.SENDIM['nagios-history']+'?host=all&archive=0&statetype=2&type=0&noflapping=on')
	print settings.SENDIM['nagios-history']+'?host=all&archive=0&statetype=2&type=0&noflapping=on'
	problemlist = []
	for line in pagehandle.readlines()[::-1] :
		if re.search( r"<img align='left'" , line ) :
			line = htmlparser.unescape( line[:-1] )

			if re.search( 'SERVICE ALERT' , line ) :
				problemlist.append( [ re.sub( r"^.*ALERT: ([^;]*);.*" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;[^;]*;([^;]*);.*$" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;[^;]*;([^;]*)<br clear='all' />$" , r"\1" , line ),
						re.sub( r".*>\[([^\]]*)\].*" , r"\1" , line ) ] )

			elif re.search( 'HOST ALERT' , line ) :
				problemlist.append( [ re.sub( r"^.*ALERT: ([^;]*);.*" , r"\1" , line ),
						"Host status",
						re.sub( r".*ALERT: [^;]*;([^;]*);.*$" , r"\1" , line ),
						re.sub( r".*ALERT: [^;]*;[^;]*;[^;]*;[^;]*;([^;]*).*<br clear='all' />$" , r"\1" , line ),
						re.sub( r".*>\[([^\]]*)\].*" , r"\1" , line ) ] )
	return problemlist

def readGraphs(host,service=None):
    try :
        if service != None : pagehandle = opener.open(www+'pnp4nagios/graph?host='+host+'&srv='+service.replace(' ' , '+')+'&view=0' )
        else : pagehandle = opener.open(www+'pnp4nagios/graph?host='+host)
    except : pass
    else:
        graphList = list()
        count = 0
        for line in pagehandle.readlines() :
            if re.match(r'<td.*Datasource:[^\<]*' , line ) :
                graphList.append( ( count, re.sub( r".*Datasource: ([^\<]*).*" , r"\1" , line ) ) )
                count+=1
        return graphList

def reloadAlert(contentMsg='') :
        print 'Insertion des alerts'
	for host,service,status,info,date in readNagios() :
		# Conversion de la date nagios en object datetime
                try : date = datetime.datetime.fromtimestamp( time.mktime( time.strptime(date, "%Y-%m-%d %H:%M:%S")) )
                except : print u"Date invalide: "+date; date = time.strftime("%Y-%m-%d %H:%M:%S")
		# Compare la liste a la BDD, si ya pas une ligne avec le meme host,service,date
		# Cause une erreur si non trouve

		# Recherche de l'hote dans BDD
		try : Host.objects.get(host=host)
		except : Host(host=host).save() ; print "Ajout de l'Host "+host

		# Recherche du service dans BDD
		try : Service.objects.get(service=service)
		except : Service(service=service).save() ; print "Ajout du service "+service

		# Recherche si l'alerte existe deja
		try : Alert.objects.get(host__host__exact=host, service__service__exact=service, date=date )
		except :
			alert = Alert(
				host = Host.objects.get(host=host),
				service = Service.objects.get(service=service),
				status = Status.objects.get(status=status),
				info=info,
				date=date
			)
			alert.save() ; print "Creation de l'Alert #"+str(alert.pk)
                        contentMsg += u"Cr\xe9ation de l'Alert #"+str(alert.pk)+" : " +alert.service.service+ " sur " +alert.host.host+ '<br>'
        return contentMsg


def treatAlerts(contentMsg='') :
    contentMsg += reloadAlert() # reloadAlert retourne un message en HTML
    ## Recherche des alerts n'ayant pas d'Event
    for alert in Alert.objects.filter(event=None) :
        try : # Execept Si pas d'alerte trouve
          lastAlert = Alert.objects.filter( Q(host=alert.host) & Q(service=alert.service) & ~Q(date__gt=alert.date) & ~Q(event=None) ).order_by('-pk')[0]
          lastEvent = lastAlert.event
          if not re.search( r"(OK|UP)", lastAlert.status.status ):
              alert.event = lastEvent ; alert.save()
              logprint("Add automaticaly Alert #" +str(alert.pk)+ " to Event #" +str(lastEvent.pk), "green")
          else : raise exceptions.StandardError
        except : 
            E = Event()
            try :
                Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service )[0]
                if re.search(r'(OK|UP)', alert.status.status) : tempStatus='WARNING'
                else : tempStatus = alert.status.status
                E.criticity= Reference.objects.filter(host__host__exact=alert.host.host, service__service__exact=alert.service.service, status__status__exact=tempStatus )[0].mail_criticity
            except : E.criticity = "?"

            try :
                Traduction.objects.filter( service__service__exact=alert.service.service )[0]
                E.message = Traduction.objects.filter(service__service__exact=alert.service)[0].traduction
            except : E.message = alert.info
            
            E.element=alert.host; E.date=alert.date
            E.save()
            alert.event = E
            alert.save()
            logprint("Link Alert #"+str(alert.pk)+" To Event #"+str(E.pk), "green")
    return contentMsg
