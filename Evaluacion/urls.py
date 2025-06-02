from django.urls import path
from .views import director_crud, estudiante_crud, docente_crud, promedios, views_estudiante, views_docente, view_director, views_reportes
app_name = 'evaluacion'
urlpatterns = [
    path('crud/estudiante/', estudiante_crud.gestion_estudiantes, name='gestion_estudiantes'),
    path('crud/directivo/', director_crud.gestion_directivo, name='gestion_directivo'),
    path('crud/docente/', docente_crud.gestion_docente, name='gestion_docente'),


    path('materias_listado/', views_estudiante.materias_estudiante_view, name='materias_estudiante'),
    path('evaluacion/<int:materia_id>/', views_estudiante.evaluar_materia, name='evaluacion_materia'),
    
    path('autoevaluacion_docente/', views_docente.autoevaluacion_docente, name='autoevaluacion_docente'),

    
    path('docentes/', view_director.listado_docentes, name='listado_docentes'),
    path('evaluar/<int:docente_id>/', view_director.evaluar_docente, name='evaluar_docente'),

    path("promedios_docente/", promedios.desempeno_por_programa, name="promedios_docente"),
    path('exportar_informe_excel/', promedios.exportar_informe_excel, name='exportar_informe_excel'),

    path('reportes/', views_reportes.reporte_selector, name='vista_reportes'),
    path('reportes/estudiantes-docente/', views_reportes.reporte_estudiantes_docente, name='reporte_estudiantes_docente'),
    path('reportes/directivos-programa/', views_reportes.reporte_directivo_programa, name='reporte_directivo_programa'),
    path('reportes/autoevaluaciones/', views_reportes.reporte_autoevaluaciones, name='reporte_autoevaluaciones'),

]