from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

from sendim.forms import UserForm

from common import logprint

@login_required
def getUsers(request) :
    Us = User.objects.all()
    if request.GET['q'] :
        Us_userN = list( Us.filter(username__icontains=request.GET['q']) )
        Us_firstN = list( Us.filter(first_name__icontains=request.GET['q']) )
        Us_lastN = list( Us.filter(last_name__icontains=request.GET['q']) )
        Us = Us_lastN + Us_firstN + Us_lastN
        print Us, Us_lastN, Us_firstN, Us_lastN
    return render(request, 'configuration/user/ul.html', {
        'Us':Us
    })

@login_required
def user(request, user_id, action="get") :
    if action == "get" :
        return render(request, 'configuration/user/user.html', {
           'U':User.objects.get(pk=user_id)
        })

    elif action == "del" :
        U = User.objects.get(pk=user_id)
        U.delete()
        return HttpResponse(str(User.objects.count())+" utilisateur(s)")

    elif action == "add" :
        U = User()
        Form = UserForm(request.POST, instance=U)
        if Form.is_valid():
            Form.save()
            U.set_password(request.POST['password'])
            U.save()
            print U.password

        return HttpResponse(str(User.objects.count())+" utilisateur(s)")

