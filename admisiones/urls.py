from django.urls import path
from .views import views_periodo, views_programa, views_pensum, views_semestre, views_materia, views_prerrequisito, views_materia_aprobada, views_matricula

urlpatterns = [
    # Vistas de Periodo
    path('periodo/', views_periodo.gestion_periodo, name='gestion_periodo'),
    path('periodo/<int:periodo_id>/', views_periodo.gestion_periodo, name='editar_periodo'),
    path('periodo/eliminar/<int:periodo_id>/', views_periodo.eliminar_periodo, name='eliminar_periodo'),

    # Vistas de Programa
    path('programa/', views_programa.gestion_programa, name='gestion_programa'),
    path('programa/eliminar/<int:programa_id>/', views_programa.eliminar_programa, name='eliminar_programa'),
    path('programa/editar/<int:programa_id>/', views_programa.gestion_programa, name='editar_programa'),

    # Vistas de Pensum
    path('pensum/', views_pensum.gestion_pensum, name='gestion_pensum'),
    path('pensum/actualizar/<int:pensum_id>/', views_pensum.gestion_pensum, name='gestion_pensum'),
    path('pensum/eliminar/<int:pensum_id>/', views_pensum.eliminar_pensum, name='eliminar_pensum'),
   

    # Vistas de Semestre
    path('semestre/', views_semestre.gestion_semestre, name='gestion_semestre'),
    path('semestre/actualizar/<int:semestre_id>/', views_semestre.actualizar_semestre, name='editar_semestre'),
    path('semestre/eliminar/<int:semestre_id>/', views_semestre.eliminar_semestre, name='eliminar_semestre'),

    # Vistas de Materia
    path('materia/', views_materia.gestion_materia, name='gestion_materia'),
    path('materia/actualizar/<int:materia_id>/', views_materia.actualizar_materia, name='editar_materia'),
    path('materia/eliminar/<int:materia_id>/', views_materia.eliminar_materia, name='eliminar_materia'),

    # Vistas de Prerrequisito
    path('prerrequisitos/', views_prerrequisito.gestion_prerrequisito, name='gestion_prerrequisito'),
    path('prerrequisitos/editar/<int:pk>/', views_prerrequisito.editar_prerrequisito, name='editar_prerrequisito'),
    path('prerrequisitos/eliminar/<int:pk>/', views_prerrequisito.eliminar_prerrequisito, name='eliminar_prerrequisito'),
    
    # Vistas de Matricula
    path('matriculas/', views_matricula.seleccionar_programa_semestre, name='seleccionar_programa_semestre'),
    path('matriculas/matricular/', views_matricula.matricular_estudiante, name='matricular_estudiante'),
    path('matriculas/inscritos/<int:materia_id>/', views_matricula.estudiantes_inscritos, name='estudiantes_inscritos'),
    path('eliminar_estudiante/<int:materia_id>/<int:estudiante_id>/', views_matricula.eliminar_estudiante, name='eliminar_estudiante'),
    path('validar_codigo/', views_matricula.validar_codigo, name='validar_codigo'),
    path('matriculas/validar_materias/', views_matricula.validar_materias, name='validar_materias'),
    path('matriculas/filtrar_estudiantes/', views_matricula.filtrar_estudiantes, name='filtrar_estudiantes'),


    # Vistas de Materia Aprobada
    path('materia_aprobada/', views_materia_aprobada.materias_por_programa_semestre, name='materias_por_programa_semestre'),
    path('materia_aprobada/<int:materia_id>/gestionar/', views_materia_aprobada.gestionar_estudiantes, name='gestionar_estudiantes'),
    path('materia_aprobada/<int:materia_id>/estados/', views_materia_aprobada.estados_estudiantes, name='estados_estudiantes'),


   
]
