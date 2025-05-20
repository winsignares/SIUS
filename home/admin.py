from django.contrib import admin
from .models.talento_humano import DetalleAcademico, DetalleExperienciaLaboral, NivelAcademico, Rol, Tarifa, TipoDocumento, Usuario, Sede, Contrato
from .models.carga_academica import CargaAcademica, Materia, Periodo, Programa, Semestre
from .models.carga_academica.datos_adicionales import  Pensum
# Register your models here.
admin.site.register(TipoDocumento)
admin.site.register(Rol)
admin.site.register(DetalleAcademico)
admin.site.register(DetalleExperienciaLaboral)
admin.site.register(NivelAcademico)
admin.site.register(Tarifa)
admin.site.register(Usuario)
admin.site.register(CargaAcademica)
admin.site.register(Materia)
admin.site.register(Periodo)
admin.site.register(Programa)
admin.site.register(Semestre)
admin.site.register(Sede)
admin.site.register(Contrato)
admin.site.register(Pensum)