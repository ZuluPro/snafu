def apropos(request) :
    """Simple about us page."""
    from django.shortcuts import render
    from django.conf import settings

    with open(settings.BASEDIR+'/../LICENSE') as text :
        license = text.read()
    return render(request, 'apropos.html', {
        'license':license
    } )
