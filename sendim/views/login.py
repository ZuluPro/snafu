"""
Login and logout views.
"""
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from sendim.forms import AuthForm

def snafu_login(request) :
    """Website login view."""
    if request.method == 'POST' :
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None :
            if user.is_active :
                login(request, user)
                return redirect('/snafu/events')
        else :
            messages.add_message(request,messages.ERROR,u"Login ou mot de passe incorrecte !")

    return render(request, 'login.html', {
    })

def snafu_logout(request) :
    """
    Website logout view.
    Redirect to login.
    """
    logout(request)
    return redirect('/snafu/login')
