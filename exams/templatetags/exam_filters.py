from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup value in dictionary by key"""
    if dictionary and key:
        return dictionary.get(key)
    return None

@register.filter
def sub(value, arg):
    """Template filter to subtract arg from value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value