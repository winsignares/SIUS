from django.contrib import admin
from .models import Estudiantes, Matricula, Prerrequisito, MateriaAprobada

# Register your models here.
admin.site.register(Estudiantes)
admin.site.register(Matricula)
admin.site.register(Prerrequisito)
admin.site.register(MateriaAprobada)