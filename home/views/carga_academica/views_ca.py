from django.shortcuts import render

def carga_academica(request):
    return render(request, 'templates/carga_academica/dashboard_ca.html')
