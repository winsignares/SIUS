from django.shortcuts import render, redirect, get_object_or_404
from Evaluacion.views.info_db import obtener_db_info
from home.models.carga_academica.carga_academica import CargaAcademica
from home.models.carga_academica.datos_adicionales import Materia, Periodo
from ..models import EvaluacionEstudiante, CategoriaEstudiante
from admisiones.models import Estudiantes, Matricula
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.timezone import now
from home.models.talento_humano.usuarios import Empleado, EmpleadoUser
from home.models.carga_academica.datos_adicionales import ProgramaUser

@login_required
def materias_estudiante_view(request):
    estudiante_model = Estudiantes.objects.get(estudiante=request.user)
    user = User.objects.get(username=estudiante_model.estudiante)
    estudiante_model.nombre_completo = user.get_full_name()
    estudiante_model.correo_personal = user.email

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    if not periodo_activo:
        messages.error(request, "No hay un período activo configurado.")
        return redirect('core:inicio')

    
    materias = Materia.objects.filter(
        matricula__estudiante=estudiante_model,
        matricula__periodo=periodo_activo,
        fk_programa=estudiante_model.programa,
    ).distinct()

    
    materias_evaluadas_ids = EvaluacionEstudiante.objects.filter(
        estudiante=estudiante_model,
        periodo=periodo_activo
    ).values_list('materia_id', flat=True)

   
    materias_no_evaluadas = materias.exclude(id__in=materias_evaluadas_ids)

    contexto = obtener_db_info(request)

    contexto.update({
        'materias': materias_no_evaluadas,
        'estudiante': estudiante_model,
        'periodo': periodo_activo,
    })

    return render(request, 'core/materias_estudiante.html', contexto)


@login_required
def evaluar_materia(request, materia_id):
    
    estudiante = get_object_or_404(Estudiantes, estudiante=request.user)
    materia = get_object_or_404(Materia, pk=materia_id)

   
    user = request.user
    estudiante.nombre_completo = user.get_full_name()
    estudiante.correo_personal = user.email

   
    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    if not periodo_activo:
        messages.error(request, "No hay un período activo configurado.")
        return redirect('evaluacion:materias_estudiante')

    # Validar que el estudiante está matriculado en la materia para el período activo
    if not Matricula.objects.filter(
        estudiante=estudiante,
        materia=materia,
        periodo=periodo_activo
    ).exists():
        messages.error(request, "La materia no pertenece al período activo.")
        return redirect('evaluacion:materias_estudiante')

    
    docentes_relacionados_ids = CargaAcademica.objects.filter(
        fk_programa=estudiante.programa,
        fk_materia=materia
    ).values_list('fk_docente_asignado', flat=True)

    if not docentes_relacionados_ids.exists():
        messages.error(request, "No hay docentes asignados a esta materia.")
        return redirect('evaluacion:materias_estudiante')

    
    try:
        docente_evaluado = Empleado.objects.get(id=docentes_relacionados_ids.first())
    except Empleado.DoesNotExist:
        messages.error(request, "No se encontró el docente asignado para esta materia.")
        return redirect('evaluacion:materias_estudiante')

   
    categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        # Procesar las respuestas del formulario
        respuestas = {}
        for key, value in request.POST.items():
            if key.startswith('respuestas[') and key.endswith(']'):
                pregunta_id = key[len('respuestas['):-1]
                respuestas[pregunta_id] = value

        if not respuestas:
            messages.error(request, "No se recibieron respuestas. Completa el formulario.")
            return redirect('evaluacion:evaluacion_materia', materia_id=materia.id)

        # Crear o actualizar la evaluación del estudiante
        EvaluacionEstudiante.objects.update_or_create(
            estudiante=estudiante,
            materia=materia,
            periodo=periodo_activo,
            docente_evaluado=docente_evaluado,
            defaults={'respuestas': respuestas}
        )

        messages.success(request, "Evaluación guardada correctamente.")
        return redirect('evaluacion:materias_estudiante')

    # Contexto para el template
    context = {
        'estudiante': estudiante,
        'materia': materia,
        'preguntas_por_categoria': preguntas_por_categoria,
        'periodo': periodo_activo,
    }
    return render(request, 'core/evaluacion_materia.html', context)