# Importar Librerías
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Importar Vistas
from .utilidades import obtener_db_info

@login_required
def reportes(request):
    contexto = obtener_db_info(request)

    return render(request, 'reportes.html', contexto)