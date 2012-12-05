from django.utils import timezone
from datetime import timedelta

def daterange(QuerySet,step='day'):
    if step == 'day' : timestep = timedelta(days=1)
    elif step == 'week' : timestep = timedelta(weeks=1)
    elif step == 'month' : timestep = timedelta(days=31)

    if QuerySet.exists() :
        start = QuerySet.order_by('date')[0].date.date()
        end = QuerySet.order_by('-date')[0].date.date()
        date = start

        while ( date <= end ) :
            yield date,QuerySet.filter(date__gte=date,date__lte=date+timestep)
            date = date + timestep

    else : yield timezone.now(), QuerySet.none()

