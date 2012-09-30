from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from sendim.forms import UserForm

from common import logprint

@login_required
def getUsers(request) :
    """Get users filtered by username, first name and last name.
    Search GET['q'] in the 3 attributes and make a logical OR.

    This view is used with AJAX.
    """
    Us = User.objects.all()
    if request.GET['q'] :
        Us = (
            set( Us.filter(username__icontains=request.GET['q']) ) |
            set( Us.filter(first_name__icontains=request.GET['q']) ) |
            set( Us.filter(last_name__icontains=request.GET['q']) )
        )

    return render(request, 'configuration/user/ul.html', {
        'Us':Us
    })

@login_required
def user(request, user_id, action="get") :
    """Get, add or delete a user.

    Delete :
     - Return user number for put it in page.

    Add :
     - user_id could be 0.
     - Return user number for put it in page.

    This view is used with AJAX."""
    if action == "get" :
        return render(request, 'configuration/user/user.html', {
           'U':get_object_or_404(User, pk=user_id)
        })

    elif action == "del" :
        U = get_object_or_404(User, pk=user_id)
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

