from django.shortcuts import render

# Create your views here.

def dashboard_carga_academica(request):
    return render(request, 'dashboard_carga_academica.html')