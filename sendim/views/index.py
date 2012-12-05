from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from sendim.models import Alert,Event
from sendim.generators import daterange
from common import logprint

from datetime import timedelta,datetime
from time import mktime, strptime
from json import dumps

@login_required
def index(request) :
    now = timezone.now()
    one_month = timedelta(days=31)

    start_date = request.GET.get('start_date', now-(12*one_month))
    end_date = request.GET.get('end_date', now+one_month)
    print start_date,end_date

    As_by_date = daterange(Event.objects.filter(date__gte=start_date,date__lte=end_date), 'month')

    As = [ (mktime(date.timetuple()),As) for (date,As) in As_by_date ]
    return render(request, 'snafu-index.html', {
      'As':As,
      'title':'Snafu'
    })

def stat(request):
    now = timezone.now()
    one_month = timedelta(days=31)

    start_date = request.GET.get('start_date', (now-(13*one_month)).strftime('%d/%m/%Y'))
    end_date = request.GET.get('end_date', (now+one_month).strftime('%d/%m/%Y'))
    print '------>',start_date,end_date

    try : start_date = datetime.strptime(start_date,'%d/%m/%Y')
    except ValueError: start_date = (now-(13*one_month)).date()
    try : end_date = datetime.strptime(end_date,'%d/%m/%Y')
    except ValueError: end_date = (now+one_month).date()
    
    print '------>',start_date,end_date
    print (end_date-start_date).days
    if not request.GET.get('step','') :
        if (end_date-start_date).days > 90: step = 'month'
        else : step = 'day'
    else : step = request.GET['step']

    As_by_date = daterange(Event.objects.filter(date__gte=start_date,date__lte=end_date), step)

    response = dumps({
      'data': [ (mktime(date.timetuple())*1000,As.count()) for (date,As) in As_by_date ],
      'bars' : { 'show': True, 'barWidth': 5000000, 'align': 'center' },
      #'lines': { 'show': True, 'steps': True },
      'points' : { 'show': True }
    })
    return HttpResponse(response, mimetype='application/json')
