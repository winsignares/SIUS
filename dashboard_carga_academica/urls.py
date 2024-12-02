from django.urls import path
from .views import dashboard_carga_academica

urlpatterns = [
    path('',dashboard_carga_academica)
]