from django.contrib import admin
from .models import CategoriaEstudiante, PreguntaEstudiante, CategoriaDocente, PreguntaDocente, CategoriaDirectivo, PreguntaDirectivo, CategoriaDocentePostgrado, PreguntaDocentePostgrado ,EvaluacionDirectivo, EvaluacionDocente, EvaluacionEstudiante, EvaluacionDocentePostgrado

admin.site.register(CategoriaEstudiante)
admin.site.register(PreguntaEstudiante)
admin.site.register(CategoriaDocente)
admin.site.register(PreguntaDocente)
admin.site.register(CategoriaDirectivo)
admin.site.register(PreguntaDirectivo)
admin.site.register(CategoriaDocentePostgrado)
admin.site.register(PreguntaDocentePostgrado)
admin.site.register(EvaluacionEstudiante)
admin.site.register(EvaluacionDocente)
admin.site.register(EvaluacionDirectivo)
admin.site.register(EvaluacionDocentePostgrado)