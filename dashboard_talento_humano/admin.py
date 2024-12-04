from django.contrib import admin
from .models import TipoDocumento, Rol, Usuario, NivelAcademico, DetalleExperienciaLaboral, DetalleAcademico, Tarifa
# Register your models here.

admin.site.register(TipoDocumento)
admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(NivelAcademico)
admin.site.register(DetalleAcademico)
admin.site.register(DetalleExperienciaLaboral)
admin.site.register(Tarifa)