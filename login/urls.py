from django.urls import path
from .views import autenticar_usuario, login

urlpatterns = [
    path('', login),
    path('autenticar_usuario/', autenticar_usuario, name='Autenticar Usuario'),
]