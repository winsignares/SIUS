from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key, None)

@register.filter
def dict_get(d, key):
    try:
        return d.get(key, None)
    except (AttributeError, TypeError):
        return None