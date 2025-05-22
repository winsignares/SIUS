from django import template

register = template.Library()

@register.filter
def contabilidad_co(value):
    try:
        return "$ {:,.0f}".format(value).replace(",", ".")
    except:
        return value

@register.filter
def miles_co(value):
    try:
        return "{:,.0f}".format(value).replace(",", ".")
    except:
        return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def celular_co(value):
    try:
        s = str(int(value)).zfill(10)
        return f"{s[:3]} {s[3:]}"
    except:
        return value

@register.filter
def fijo_co(value):
    try:
        s = str(int(value)).zfill(7)
        return f"{s[:3]} {s[3:]}"
    except:
        return value