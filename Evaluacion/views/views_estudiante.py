from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia
from ..models import PreguntaEstudiante, EvaluacionEstudiante, CategoriaEstudiante
from admisiones.models import Estudiantes, Matricula
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User


@login_required
def materias_estudiante_view(request):
    estudiante_model = Estudiantes.objects.get(estudiante=request.user)

    user = User.objects.get(username=estudiante_model.estudiante)
    estudiante_model.nombre_completo = user.get_full_name()  
    estudiante_model.correo_personal = user.email  
      
    # Todas las materias donde el estudiante está matriculado
    materias = Materia.objects.filter(
        matricula__estudiante=estudiante_model,
        fk_programa=estudiante_model.programa,
        fk_semestre=estudiante_model.semestre
    ).distinct()

    # Obtener materias ya evaluadas por el estudiante (si respondió alguna pregunta de esa materia)
    materias_evaluadas_ids = EvaluacionEstudiante.objects.filter(
        estudiante=estudiante_model
    ).values_list('materia_id', flat=True).distinct()

    # Excluir materias ya evaluadas
    materias_no_evaluadas = materias.exclude(id__in=materias_evaluadas_ids)

    return render(request, 'core/materias_estudiante.html', {
        'materias': materias_no_evaluadas,
        'estudiante': estudiante_model,
    })

@login_required
def evaluar_materia(request, materia_id):
    estudiante = get_object_or_404(Estudiantes, estudiante=request.user)
    materia = get_object_or_404(Materia, pk=materia_id)

    categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        pregunta_ids = request.POST.getlist('pregunta_id')

        evaluaciones_existentes = EvaluacionEstudiante.objects.filter(
            estudiante=estudiante,
            materia=materia,
            pregunta_id__in=pregunta_ids
        ).values_list('pregunta_id', flat=True)

        nuevas_evaluaciones = 0

        for pregunta_id in pregunta_ids:
            if int(pregunta_id) in evaluaciones_existentes:
                continue  # Ya existe, no la guarda de nuevo

            respuesta = request.POST.get(f'respuesta_{pregunta_id}')
            if respuesta is not None:
                EvaluacionEstudiante.objects.create(
                    estudiante=estudiante,
                    materia=materia,
                    pregunta_id=pregunta_id,
                    respuesta=respuesta
                )
                nuevas_evaluaciones += 1

        if nuevas_evaluaciones == 0:
            messages.warning(request, "Ya has realizado esta evaluación previamente.")
        else:
            messages.success(request, "Evaluación registrada correctamente.")

        return redirect('evaluacion:materias_estudiante')

    context = {
        'estudiante': estudiante,
        'materia': materia,
        'preguntas_por_categoria': preguntas_por_categoria,
    }
    return render(request, 'core/evaluacion_materia.html', context)