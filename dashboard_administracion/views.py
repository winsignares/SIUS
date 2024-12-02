from django.shortcuts import render

# Create your views here.

def dashboard_administracion(request):
    return render(request, 'dashboard_administracion.html')