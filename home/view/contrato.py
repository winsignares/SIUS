# Importar Librerías
from datetime import datetime
from django.shortcuts import render


# Importar Vistas
from .utilidades import obtener_db_info

# Importar Módelos
from home.models import Empleado, Programa


def gestion_contratos_docentes(request):
    """
    Muestra el módulo de contratos (Dpto Contablilidad)
    """
    contexto = obtener_db_info(
        request,
        incluir_datos_adicionales=True
    )

    contexto.update({
        'programa_list': Programa.objects.all(),
    })

    return render(
        request,
        'docentes.html',
        contexto
    )


def gestion_contratos_administrativos(request):
    """
    Muestra el módulo de administrativos (Dpto Contablilidad)
    """
    contexto = obtener_db_info(
        request,
        incluir_datos_adicionales=True
    )

    # Filtrar usuarios con rol de administrativo
    administrativos = Empleado.objects.filter(
        fk_rol__descripcion="Administrativo"
    ).order_by(
        '-fecha_modificacion'
    )

    # Agregar los administrativos al contexto
    contexto.update({
        "administrativos": administrativos,
        "dia_actual": datetime.now().date(),
    })

    return render(
        request,
        'administrativos.html',
        contexto
    )
