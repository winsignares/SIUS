from django.shortcuts import render

def administracion(request):
    return render(request, 'templates/administracion/dashboard_admin.html')
