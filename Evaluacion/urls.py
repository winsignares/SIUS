from django.urls import path
from .views import views_crud_evaluacion, views_estudiante
app_name = 'evaluacion'
urlpatterns = [
    path('', views_crud_evaluacion.gestion_roles, name='gestion_roles'),
    path('crear_categoria/', views_crud_evaluacion.crear_categoria, name='crear_categoria'),
    path('crear_pregunta/', views_crud_evaluacion.crear_pregunta, name='crear_pregunta'),
    path('editar_pregunta/', views_crud_evaluacion.editar_pregunta, name='editar_pregunta'),
    path('editar_categoria/', views_crud_evaluacion.editar_categoria, name='editar_categoria'),
    path('eliminar_categoria/', views_crud_evaluacion.eliminar_categoria, name='eliminar_categoria'),


    path('materias_listado/', views_estudiante.materias_estudiante_view, name='materias_estudiante'),
    path('evaluacion/<int:estudiante_id>/<int:materia_id>/', views_estudiante.evaluar_materia, name='evaluacion_materia'),
    
    

]