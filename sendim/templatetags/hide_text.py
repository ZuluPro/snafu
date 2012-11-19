from django import template
from re import sub

register = template.Library()

@register.filter(name='hide_text')
def hide_text(text, repl='*') :
    """
    """
    return sub(r'.', repl, text)
