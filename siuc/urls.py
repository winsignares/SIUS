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

urlpatterns = [
    path('root/', admin.site.urls),
    
    path('siuc/login/',views.iniciar_sesion_form, name="iniciar_sesion_form"),
    path('siuc/login/ingresar/',views.signin, name="signin"),
    
    path('siuc/restablecer_contraseña/',views.restablecer_contraseña_form, name="restablecer_contraseña_form"),
    path('siuc/restablecer_contraseña/actualizar/',views.actualizar_contraseña, name="actualizar_contraseña"),
    
    path('siuc/dashboard/inicio/', views.dashboard, name='dashboard'),
    path("siuc/dashboard/gestion_aspirantes/", views.gestion_aspirantes, name="gestion_aspirantes"),
    path("siuc/dashboard/gestion_empleados/", views.gestion_empleados, name="gestion_empleados"),
    path("siuc/dashboard/reportes/", views.reportes, name="reportes"),
    path('siuc/logout/', views.cerrar_sesion, name='cerrar_sesion')
]