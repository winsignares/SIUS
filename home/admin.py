from django.contrib import admin
from .models.talento_humano import NivelAcademico, Rol, TipoDocumento, Sede, Contrato, NivelAcademicoHistorico, EmpleadoUser, Empleado
from .models.talento_humano.datos_adicionales import Departamento, EPS, ARL, AFP, CajaCompensacion
from .models.carga_academica import CargaAcademica, Materia, Periodo, Programa, Semestre, ProgramaUser, Pensum
# Register your models here.
admin.site.register(TipoDocumento)
admin.site.register(Rol)
admin.site.register(NivelAcademico)
admin.site.register(EmpleadoUser)
admin.site.register(CargaAcademica)
admin.site.register(Materia)
admin.site.register(Periodo)
admin.site.register(Programa)
admin.site.register(ProgramaUser)
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
admin.site.register(Empleado)