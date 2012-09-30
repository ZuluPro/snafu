from sendim.models import *
from django import template

register = template.Library()

@register.filter(name='addFontColor', is_safe=True)
def addFontColor(value, arg) :
    """Return the given string between <font>...</font> markup.
    string is colorized by the color given in arg."""

    for color,status in ( ('green','UP'), ('green','OK'), ('red','CRITICAL'), ('red','DOWN'), ('gold','WARNING'), ('violet','UNKNOWN') ) :
        if arg == status : return '<font color='+color+'>'+value+'</font>'
