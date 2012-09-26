from django.conf import settings

from sendim.models import *
from sendim.defs import addMail,opengraph
from referentiel.models import *

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def makeMail(E):
    R = E.getPrimaryAlert().reference
    MT = MailTemplate.objects.get(choosen=True)
    msg = {}
    msg['from'] = settings.SNAFU['smtp-from']
    msg['to'] = R.mail_group.to
    if E.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
    msg['cc'] = ' ,'.join( [  settings.SNAFU['smtp-from'], R.mail_group.cc] )
    msg['subject'] = MT.subject 
    msg['body'] = MT.body
    
    return msg

def sendMail(POST) :
    E = Event.objects.get(pk=POST['eventPk'])
    A = E.getPrimaryAlert()
    # Recherche du MailGroup correspondant
    R = A.reference

    msg = MIMEMultipart()
    msg['From'] = settings.SNAFU['smtp-from']
    msg['To'] = POST['to']
    if POST['ccm'] : msg['To'] += ', '+ R.mail_group.ccm
 
    mailSub = POST['subject']
    mailText = POST['body']

    subs = (
        ("$HOST$", A.host.host),
        ("$MESSAGE$", E.message),
        ("$MAIL_TYPE$", R.mail_type.mail_type),
        ("$CRITICITY$", E.criticity),
        ("$GLPI$" , str(E.glpi)),
        ("$GLPI-URL$", settings.SNAFU['glpi-url']+'front/ticket.form.php?id='),
        ("$TRADUCTION$", E.message),
        ("$DATE$", E.date.strftime('%d/%m/%y - %H:%M:%S')),
        ("$JOUR$", E.date.strftime('%d/%m/%y')),
        ("$HEURE$", E.date.strftime('%H:%M:%S')),
        ("$LOG$" , '\n'.join( [ A.date.strftime('%d/%m/%y %H:%M:%S - ')+A.service.service+' en ' +A.status.status+' - '+A.info for A in E.getAlerts() ] ) )
    ) 
    for pattern,string in subs :
        mailText = mailText.replace(pattern, string)
        mailSub = mailSub.replace(pattern, string)
    msg['Subject'] = mailSub
    msg.attach( MIMEText( mailText.encode('utf8') , 'plain' ) )
    
    # Ajout des graphs slelectinnes
    if 'graphList' in POST :
        graphList = POST.getlist('graphList')
        for i in range(len(graphList)) :
            pagehandle = opengraph(A, graphList[i][0])
            pagehandle2 = opengraph(A, graphList[i][0])
            msg.attach( MIMEImage( pagehandle ) )
            msg.attach( MIMEImage( pagehandle2 ) )
            logprint("Add " +graphList[i]+ "to mail" )

    smtpObj = smtplib.SMTP(settings.SNAFU['smtp-server'] , settings.SNAFU['smtp-port'] )
    if 'smtp-password' in settings.SNAFU.keys() :
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(settings.SNAFU['smtp-from'], settings.SNAFU['smtp-password'])
    smtpObj.sendmail( msg['From'] , ( msg['To'], msg['Cc'] ), msg.as_string() )

    E.mail = True
    E.save()
    msg['body'] = mailText
    addMail(E.glpi, msg)

