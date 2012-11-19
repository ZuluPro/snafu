from django.db import models

class MailTemplate(models.Model) :
    subject = models.CharField(max_length=200)
    body = models.CharField(max_length=2000)
    comment = models.CharField(max_length=300, blank=True,null=True)
    chosen = models.BooleanField(default=False)

    class Meta:
        app_label = 'sendim'

    def setOn(self):
        """Set template as used, set all others not."""
        previousMT = MailTemplate.objects.get(chosen=True)
        previousMT.chosen = False
        previousMT.save()
        self.chosen = True
        self.save()

    def getOn():
        """Return the chosen template."""
        return MailTemplate.objects.get(chosen=True)

    def __unicode__(self):
        return str(self.pk)
