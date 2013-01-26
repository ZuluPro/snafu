from django.db import models

class MailTemplate_Manager(models.Manager):
    def get_or_set_active(self, *args, **kwargs):
        """
        If there's no chosen Mail Template, choose the first.
        """
        # Try to find supervisor arg and corresponding object by name
        if not super(MailTemplate_Manager, self).get_query_set().filter(chosen=True).exists() :
            MailTemplate.objects.get(pk=1).set_active()
        return super(MailTemplate_Manager, self).get_query_set().filter(chosen=True)

    def get_active(self):
        """Return the chosen template."""
        return super(MailTemplate_Manager, self).get_query_set().get(chosen=True)

class MailTemplate(models.Model) :
    """
    Used for save a standard mail.
    Multiples variables can be used for make it dynamic.
    You have a list of thoses variables below :
     - $HOST$ : Hostname
     - $MESSAGE$ : Event's message
     - $MAIL_TYPE$ : Incident type
     - $CRITICITY$ : Incident criticity
     - $GLPI$ : GLPI ticket's number
     - $GLPI-URL$ : GLPI server's URL
     - $DATETIME$ : Date and hour
     - $DATE$ : Date
     - $TIME$ : Hour
     - $LOG$ : Alerts' log lines
    """
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    body = models.CharField(max_length=2000, verbose_name="Corps")
    comment = models.CharField(max_length=300, blank=True,null=True, verbose_name="Commentaire")
    chosen = models.BooleanField(default=False, verbose_name=u"Utilis\xe9")

    objects = MailTemplate_Manager()
    class Meta:
        app_label = 'sendim'

    def set_active(self):
        """Set template as used, set all others as not."""
        MailTemplate.objects.exclude(pk=self.pk).update(chosen=False)
        MailTemplate.objects.filter(pk=self.pk).update(chosen=True)

    def __unicode__(self):
        return str(self.pk)

    def delete(self, *args, **kwargs):
        if self.chosen == True :
            MailTemplate.objects.get(pk=1).set_active()
        super(MailTemplate, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.chosen == True :
            self.set_active()
        super(MailTemplate, self).save(*args, **kwargs)
