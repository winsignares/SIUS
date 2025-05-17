from django.contrib import admin
from .models import CategoriaEstudiante, PreguntaEstudiante, CategoriaDocente, PreguntaDocente, CategoriaDirectivo, PreguntaDirectivo

admin.site.register(CategoriaEstudiante)
admin.site.register(PreguntaEstudiante)
admin.site.register(CategoriaDocente)
admin.site.register(PreguntaDocente)
admin.site.register(CategoriaDirectivo)
admin.site.register(PreguntaDirectivo)

