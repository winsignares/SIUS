from django.urls import path
from .views import dashboard_administracion

urlpatterns = [
    path('',dashboard_administracion)
]