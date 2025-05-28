# Importar Librerias
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Importar Vistas
from .utilidades import obtener_db_info



@login_required
def dashboard(request):
    '''
        Función para mostrar el dashboard cuando un usuario inicia sesión.
    '''
    contexto = obtener_db_info(request)

    return render(request, 'dashboard.html', contexto)