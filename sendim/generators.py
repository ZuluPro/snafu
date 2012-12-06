from django.utils.timezone import now
from datetime import timedelta

def daterange(QuerySet,step='day'):
    """
    Yield elements by step given in argument.
    Work for models with 'date' field as Alert or Event.
    """
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

    else : yield now(), QuerySet.none()

