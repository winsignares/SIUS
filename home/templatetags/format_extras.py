from django import template
from home.models.talento_humano.contrato import Contrato

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

@register.filter
def dedicacion_docente(docente):
    contrato = Contrato.objects.filter(fk_usuario=docente, vigencia_contrato=True).order_by('-fecha_inicio').first()
    return contrato.fk_dedicacion.nombre_corto if contrato and contrato.fk_dedicacion else None