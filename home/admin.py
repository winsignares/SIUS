from django.contrib import admin
from .models.talento_humano import DetalleAcademico, DetalleExperienciaLaboral, NivelAcademico, Rol, Tarifa, TipoDocumento, Usuario

# Register your models here.
admin.site.register(TipoDocumento)
admin.site.register(Rol)
admin.site.register(DetalleAcademico)
admin.site.register(DetalleExperienciaLaboral)
admin.site.register(NivelAcademico)
admin.site.register(Tarifa)
admin.site.register(Usuario)