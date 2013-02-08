"""
Login and logout views.
"""
from django.shortcuts import render, redirect
from sendim.forms import AuthForm

def snafu_login(request) :
    """Website login view."""
    from django.contrib.auth import authenticate, login
    from django.contrib import messages

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
    from django.contrib.auth import logout

    logout(request)
    return redirect('/snafu/login')
