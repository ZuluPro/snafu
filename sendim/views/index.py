from django.contrib.auth.decorators import login_required

from datetime import timedelta,datetime

@login_required
def index(request) :
    from django.shortcuts import render
    from sendim.generators import daterange

    now = now()
    one_month = timedelta(days=31)

    start_date = request.GET.get('start_date', now-(12*one_month))
    end_date = request.GET.get('end_date', now+one_month)

    As_by_date = daterange(Event.objects.filter(date__gte=start_date,date__lte=end_date), 'month')

    As = [ (mktime(date.timetuple()),As) for (date,As) in As_by_date ]
    return render(request, 'snafu-index.html', {
      'As':As,
      'title':'Snafu'
    })

def stat(request):
    from django.http import HttpResponse
    from sendim.models import Event
    from time import mktime, strptime
    from json import dumps

    now = now()
    one_month = timedelta(days=31)

    start_date = request.GET.get('start_date', (now-(13*one_month)).strftime('%d/%m/%Y'))
    end_date = request.GET.get('end_date', (now+one_month).strftime('%d/%m/%Y'))

    try : start_date = datetime.strptime(start_date,'%d/%m/%Y')
    except ValueError: start_date = (now-(13*one_month)).date()
    try : end_date = datetime.strptime(end_date,'%d/%m/%Y')
    except ValueError: end_date = (now+one_month).date()
    
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
