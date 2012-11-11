from django.db import models

class SupervisorType(models.Model) :
    name = models.CharField(max_length=30)
    
    class Meta:
        app_label = 'sendim'

    def __unicode__(self):
        return self.name

class Supervisor(models.Model) :
    name = models.CharField(max_length=200)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    index = models.URLField()
    status = models.URLField()
    history = models.URLField()
    active = models.BooleanField(default=True)
    supervisor_type = models.ForeignKey(SupervisorType, default=1)

    class Meta:
        app_label = 'sendim'
    
    def getOpener():
        passman = HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.index, self.login, self.password)
        authhandler = HTTPBasicAuthHandler(passman)
        opener = build_opener(authhandler)
        install_opener(opener)
        return opener

    def __unicode__(self):
        return self.name


