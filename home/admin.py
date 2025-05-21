from django.contrib import admin
from .models.talento_humano import DetalleAcademico, DetalleExperienciaLaboral, NivelAcademico, Rol, Tarifa, TipoDocumento, Empleado, Sede, Contrato, NivelAcademicoHistorico, EmpleadoUser
from .models.talento_humano.datos_adicionales import Departamento, EPS, ARL, AFP, CajaCompensacion
from .models.carga_academica import CargaAcademica, Materia, Periodo, Programa, Semestre
from .models.carga_academica.datos_adicionales import Pensum
# Register your models here.
admin.site.register(TipoDocumento)
admin.site.register(Rol)
admin.site.register(DetalleAcademico)
admin.site.register(DetalleExperienciaLaboral)
admin.site.register(NivelAcademico)
admin.site.register(Tarifa)
admin.site.register(Empleado)
admin.site.register(EmpleadoUser)
admin.site.register(CargaAcademica)
admin.site.register(Materia)
admin.site.register(Periodo)
admin.site.register(Programa)
admin.site.register(Semestre)
admin.site.register(Sede)
admin.site.register(Pensum)
admin.site.register(Contrato)
admin.site.register(NivelAcademicoHistorico)
admin.site.register(Departamento)
admin.site.register(EPS)
admin.site.register(ARL)
admin.site.register(AFP)
admin.site.register(CajaCompensacion)