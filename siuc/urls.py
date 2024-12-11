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
    path('siuc/login/',views.welcome, name="welcome"),
    path('siuc/login/iniciar_sesion/',views.iniciar_sesion, name="iniciar_sesion"),
    path('siuc/login/actualizar_contraseña/',views.actualizar_contraseña, name="actualizar_contraseña"),
    
    path('siuc/dashboard/', views.dashboard, name='dashboard' ),
    path('siuc/logout/', views.cerrar_sesion, name='cerrar_sesion')
    
]