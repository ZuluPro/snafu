from django.db import models

class MailTemplate(models.Model) :
    subject = models.CharField(max_length=200)
    body = models.CharField(max_length=2000)
    comment = models.CharField(max_length=300, blank=True,null=True)
    chosen = models.BooleanField(default=False)

    class Meta:
        app_label = 'sendim'

    def set_active(self):
        """Set template as used, set all others as not."""
        for MT in MailTemplate.objects.all():
            MT.chosen = False
            MT.save()
        self.chosen = True
        self.save()

    def get_active():
        """Return the chosen template."""
        return MailTemplate.objects.get(chosen=True)

    def __unicode__(self):
        return str(self.pk)

    def delete(self, *args, **kwargs):
        if self.chosen == True :
            MailTemplate.objects.get(pk=1).set_active()
        super(MailTemplate, self).delete(*args, **kwargs)
