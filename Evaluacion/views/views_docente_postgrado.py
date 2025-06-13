from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Evaluacion.views.info_db import obtener_db_info
from home.models.talento_humano.usuarios import EmpleadoUser
from ..models import CategoriaDocentePostgrado, EvaluacionDocentePostgrado
from django.utils.timezone import now
from home.models.carga_academica.datos_adicionales import Periodo

@login_required
def autoevaluacion_docente_postgrado(request):
    usuario = request.user

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    if not periodo_activo:
        messages.error(request, "No hay un período activo configurado.")
        return redirect('core:inicio')

    categorias = CategoriaDocentePostgrado.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    empleado = EmpleadoUser.objects.get(fk_user=usuario).fk_empleado

    ya_evaluado = EvaluacionDocentePostgrado.objects.filter(
        docente=empleado,
        periodo=periodo_activo
    ).exists()

    if request.method == 'POST':
        if ya_evaluado:
            messages.warning(request, "Ya realizaste esta autoevaluación para el período activo.")
            return redirect('evaluacion:autoevaluacion_docente_postgrado')

        respuestas = {}
        for key, value in request.POST.items():
            if key.startswith('respuesta_'):
                pregunta_id = key.replace('respuesta_', '')
                respuestas[pregunta_id] = int(value)

        if not respuestas:
            messages.error(request, "No se registraron evaluaciones.")
            return redirect('evaluacion:autoevaluacion_docente_postgrado')

        EvaluacionDocentePostgrado.objects.create(
            docente=empleado,
            periodo=periodo_activo,
            respuestas=respuestas
        )

        messages.success(request, "Autoevaluación registrada correctamente.")
        return redirect('evaluacion:seleccion_autoevaluacion_docente')

    contexto = obtener_db_info(request)

    contexto.update({
        'docente': empleado,
        'preguntas_por_categoria': preguntas_por_categoria,
        'ya_evaluado': ya_evaluado,
        'periodo': periodo_activo,
    })
    return render(request, 'core/autoevaluacion_docente_postgrado.html', contexto)