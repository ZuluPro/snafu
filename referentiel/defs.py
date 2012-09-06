from referentiel.models import Reference, Host, Service, Status

def getReference(A, byHost=True, byService=True, byStatus=True ) :
    Rs = Reference.objects.all()
    if byHost : Rs = Rs.filter(host=A.host)
    if byService : Rs = Rs.filter(service=A.service)
    if byStatus : Rs = Rs.filter(status=A.status)

    if not Rs : R = None
    else : R = Rs[0]

    return R
