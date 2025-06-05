from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now

from Evaluacion.views.info_db import obtener_db_info
from Evaluacion.models import EvaluacionDocente, EvaluacionDocentePostgrado
from home.models.carga_academica.datos_adicionales import Periodo, Programa
from home.models.carga_academica.carga_academica import CargaAcademica
from home.models.talento_humano.usuarios import EmpleadoUser


@login_required
def seleccion_autoevaluacion_docente(request):
    user = request.user

    # Obtener el empleado asociado al usuario
    try:
        empleado = EmpleadoUser.objects.get(fk_user=user).fk_empleado
    except EmpleadoUser.DoesNotExist:
        messages.error(request, "No se encontró información del empleado asociada a tu usuario.")
        return redirect('dashboard')

    
    cargas = CargaAcademica.objects.select_related('fk_programa').filter(fk_docente_asignado=empleado)

   
    niveles = set(carga.fk_programa.nivel_formacion.upper() for carga in cargas if carga.fk_programa and carga.fk_programa.nivel_formacion)

    tiene_pregrado = "PREGRADO" in niveles
    tiene_postgrado = "POSTGRADO" in niveles

    if not (tiene_pregrado or tiene_postgrado):
        messages.warning(request, "No tienes programas en tu carga académica con nivel de formación PREGRADO o POSTGRADO.")
        return redirect('dashboard')

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    ya_evaluo_pregrado = False
    ya_evaluo_postgrado = False

    if periodo_activo:
        if tiene_pregrado:
            ya_evaluo_pregrado = EvaluacionDocente.objects.filter(docente=empleado, periodo=periodo_activo).exists()
        if tiene_postgrado:
            ya_evaluo_postgrado = EvaluacionDocentePostgrado.objects.filter(docente=empleado, periodo=periodo_activo).exists()

    contexto = obtener_db_info(request)
    contexto.update({
        'tiene_pregrado': tiene_pregrado,
        'tiene_postgrado': tiene_postgrado,
        'ya_evaluo_pregrado': ya_evaluo_pregrado,
        'ya_evaluo_postgrado': ya_evaluo_postgrado,
    })

    return render(request, 'core/seleccion_autoevaluacion_docente.html', contexto)
