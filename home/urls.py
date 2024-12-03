from django.urls import path
from .views import login, dashboard

urlpatterns = [
    path('login/', login),
    path('dashboard/', dashboard)
]