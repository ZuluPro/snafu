from referentiel.models import Reference, Traduction, Host, Service, Status

def getReference(A, byHost=True, byService=True, byStatus=True ) :
    Rs = Reference.objects.all()
    if byHost : Rs = Rs.filter(host=A.host)
    if byService : Rs = Rs.filter(service=A.service)
    if byStatus : Rs = Rs.filter(status=A.status)

    if not Rs : R = None ; logprint('No Reference for Alert #'+str(self.pk), 'red')
    else : R = Rs[0]

    return R

def getTraduction(A, byStatus=True ) :
    Ts = Traduction.objects.all()
    if byStatus : Ts = Ts.filter(status=A.status)

    if not Ts : T = None
    else : T = Ts[0]

    return T
