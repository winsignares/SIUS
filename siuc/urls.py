"""
URL configuration for siuc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views
from django.conf.urls import handler404
from home.views import detalle_usuario


urlpatterns = [
    path('root/', admin.site.urls),
    
    path('siuc/login/',views.iniciar_sesion_form, name="iniciar_sesion_form"),
    path('siuc/login/ingresar/',views.signin, name="signin"),
    
    path('siuc/restablecer_contraseña/',views.restablecer_contraseña_form, name="restablecer_contraseña_form"),
    path('siuc/restablecer_contraseña/actualizar/',views.actualizar_contraseña, name="actualizar_contraseña"),
    
    path('siuc/dashboard/inicio/', views.dashboard, name='dashboard'),
    
    path("siuc/dashboard/gestion_aspirantes/", views.gestion_aspirantes, name="gestion_aspirantes"),
    path("siuc/dashboard/gestion_aspirantes/agregar_info_personal/", views.agregar_info_personal, name="agregar_info_personal"),
    path("siuc/dashboard/gestion_aspirantes/agregar_exp_laboral/", views.agregar_exp_laboral, name="agregar_exp_laboral"),
    path("siuc/dashboard/gestion_aspirantes/agregar_detalle_academico/", views.agregar_detalle_academico, name="agregar_detalle_academico"),
    
    
    
    path("siuc/dashboard/gestion_empleados/", views.gestion_empleados, name="gestion_empleados"),
    
    path("siuc/dashboard/reportes/", views.reportes, name="reportes"),    
    path("siuc/dashboard/reporte/excel", views.generar_reporte_excel, name="reporte_excel"),
    path('cargar_empleados/', views.cargar_empleados_masivamente, name='cargar_empleados'),
    path('siuc/dashboard/detalle_usuario/<str:tipo>/<int:usuario_id>/', detalle_usuario, name='detalle_usuario'),
    
    path("siuc/dashboard/editar_usuario/<str:tipo>/<int:usuario_id>/", views.editar_usuario, name="editar_usuario"),
    # path("siuc/dashboard/guardar_usuario/<str:tipo>/<int:usuario_id>/", views.guardar_usuario, name="guardar_usuario"),
    path("siuc/dashboard/guardar_usuario/<str:tipo>/<int:usuario_id>/", views.guardar_usuario, name="guardar_usuario"),


    path('siuc/logout/', views.cerrar_sesion, name='cerrar_sesion')
]

# Error 404 personalizado
handler404 = 'home.views.error_404_view'
