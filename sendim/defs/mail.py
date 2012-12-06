from django.conf import settings

from sendim.models import Event, MailTemplate
from sendim.defs import addMail, opengraph

from smtplib import SMTP
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# MOVE INTO EVENT
def makeMail(E):
    """
    Using the given Event and the chosen MailTemplate for create
    a dictionnary which contains all mail attributes.
    """
    R = E.getPrimaryAlert().reference
    if MailTemplate.objects.filter(chosen=True).exists() :
        MT = MailTemplate.objects.get(chosen=True)
    else :
        MT = MailTemplate.objects.get(pk=1)

    msg = {}
    msg['from'] = settings.SNAFU['smtp-from']
    msg['to'] = R.mail_group.to
    if E.criticity == 'Majeur' : msg['to'] += ', '+ R.mail_group.ccm
    msg['cc'] = ' ,'.join( [  settings.SNAFU['smtp-from'], R.mail_group.cc] )
    msg['subject'] = MT.subject 
    msg['body'] = MT.body
    
    return msg

def sendMail(POST) :
    """
    Use request.POST from 'sendim/templates/event/preview-mail.html',
    for send an email.
    This function make all substitutions before processing.
    After send, add mail to GLPI ticket.
    """
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
        ("$HOST$", A.host.name),
        ("$MESSAGE$", E.message),
        ("$MAIL_TYPE$", R.mail_type.name),
        ("$CRITICITY$", E.criticity),
        ("$GLPI$" , str(E.glpi)),
        ("$GLPI-URL$", settings.SNAFU['glpi-url']+'front/ticket.form.php?id='),
        ("$TRADUCTION$", E.message),
        ("$DATE$", E.date.strftime('%d/%m/%y - %H:%M:%S')),
        ("$JOUR$", E.date.strftime('%d/%m/%y')),
        ("$HEURE$", E.date.strftime('%H:%M:%S')),
        ("$LOG$" , '\n'.join( [ A.date.strftime('%d/%m/%y %H:%M:%S - ')+A.service.name+' en ' +A.status.name+' - '+A.info for A in E.getAlerts() ] ) )
    ) 
    for pattern,string in subs :
        mailText = mailText.replace(pattern, string)
        mailSub = mailSub.replace(pattern, string)
    msg['Subject'] = mailSub
    msg.attach( MIMEText( mailText.encode('utf8') , 'plain' ) )
    
    # Ajout des graphs selectinnes
    if 'graphList' in POST :
        graphList = POST.getlist('graphList')
        for i in range(len(graphList)) :
            pagehandle = opengraph(A, graphList[i])
            #pagehandle2 = opengraph(A, graphList[i][0])
            msg.attach( MIMEImage( pagehandle ) )
            #msg.attach( MIMEImage( pagehandle2 ) )

    smtpObj = SMTP(settings.SNAFU['smtp-server'] , settings.SNAFU['smtp-port'] )
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

    return True
