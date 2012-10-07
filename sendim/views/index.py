from django.shortcuts import render
from sendim.models import *
from common import logprint

from time import mktime
from datetime import datetime

def index(request) :
    D = datetime.now()
    if D.month == 1 : month=12 ; year=D.year-1
    else : month=D.month-1 ; year=D.year

    monthAs = {}
    for E in Event.objects.filter(date__gte=D.replace(month=month,year=year) ) :
        _date = mktime( E.date.date().timetuple() )
        if not _date in monthAs : monthAs[_date] = 1
        else : monthAs[_date] = monthAs[_date]+1

    monthAs = monthAs.items()
    monthAs.sort()

    return render(request, 'snafu-index.html', {
      'monthAs' : monthAs
    })

