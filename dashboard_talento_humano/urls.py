from django.urls import path
from .views import dashboard_talento_humano

urlpatterns = [
    path('',dashboard_talento_humano)
]