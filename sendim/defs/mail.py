from django.conf import settings

from sendim.models import Event, MailTemplate
from sendim.defs import addMail, opengraph

from smtplib import SMTP
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

    # Make substitutions
    SUBS = (
        ("$HOST$", A.host.name),
        ("$MESSAGE$", E.message),
        ("$MAIL_TYPE$", R.mail_type.name),
        ("$CRITICITY$", E.criticity),
        ("$GLPI$" , str(E.glpi)),
        ("$GLPI-URL$", settings.SNAFU['glpi-url']+'front/ticket.form.php?id='),
        ("$TRANSLATION", E.message),
        ("$DATETIME$", E.date.strftime('%d/%m/%y - %H:%M:%S')),
        ("$DATE$", E.date.strftime('%d/%m/%y')),
        ("$TIME$", E.date.strftime('%H:%M:%S')),
        ("$LOG$" , '\n'.join( [ A.date.strftime('%d/%m/%y %H:%M:%S - ')+A.service.name+' en ' +A.status.name+' - '+A.info for A in E.getAlerts() ] ) )
    ) 
    for pattern,string in SUBS :
        mailText = mailText.replace(pattern, string)
        mailSub = mailSub.replace(pattern, string)
    msg['Subject'] = mailSub
    msg.attach( MIMEText( mailText.encode('utf8') , 'plain' ) )
    
    # Add graph to mail
    if 'graphList' in POST :
        graphList = POST.getlist('graphList')
        for i in range(len(graphList)) :
            pagehandle = opengraph(A, graphList[i])
            #pagehandle2 = opengraph(A, graphList[i][0])
            msg.attach( MIMEImage( pagehandle ) )
            #msg.attach( MIMEImage( pagehandle2 ) )

    # Send mail
    smtpObj = SMTP(settings.SNAFU['smtp-server'] , settings.SNAFU['smtp-port'] )
    if 'smtp-password' in settings.SNAFU.keys() :
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(settings.SNAFU['smtp-from'], settings.SNAFU['smtp-password'])
    smtpObj.sendmail( msg['From'] , ( msg['To'], msg['Cc'] ), msg.as_string() )

    Event.objects.filter(pk=E.pk).update(mail=True)
    msg['body'] = mailText
    addMail(E.glpi, msg)

    return True
