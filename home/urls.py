from django.urls import path
from .views import administracion, carga_academica, director_talento_humano, secretaria_talento_humano

urlpatterns = [
    path('administracion/', administracion),
    path('carga_academica/', carga_academica),
    path('talento_humano/director', director_talento_humano),
    path('talento_humano/secretaria', secretaria_talento_humano)
]