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

    
    materias = Materia.objects.filter(
        matricula__estudiante=estudiante_model,
        fk_programa=estudiante_model.programa,
        fk_semestre=estudiante_model.semestre
    ).distinct()

   
    materias_evaluadas_ids = EvaluacionEstudiante.objects.filter(
        estudiante=estudiante_model
    ).values_list('materia_id', flat=True)

   
    materias_no_evaluadas = materias.exclude(id__in=materias_evaluadas_ids)

    return render(request, 'core/materias_estudiante.html', {
        'materias': materias_no_evaluadas,
        'estudiante': estudiante_model,
    })

 # Para pruebas rápidas de salida (opcional)

@login_required
def evaluar_materia(request, materia_id):
    estudiante = get_object_or_404(Estudiantes, estudiante=request.user)
    materia = get_object_or_404(Materia, pk=materia_id)

    user = User.objects.get(username=estudiante.estudiante)
    estudiante.nombre_completo = user.get_full_name()  
    estudiante.correo_personal = user.email  


    categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        respuestas = {}
        for key, value in request.POST.items():
            if key.startswith('respuestas[') and key.endswith(']'):
                # Extraer el id de la pregunta entre los corchetes
                pregunta_id = key[len('respuestas['):-1]
                respuestas[pregunta_id] = value

        if not respuestas:
            messages.error(request, "No se recibieron respuestas. Completa el formulario.")
            return redirect('evaluacion:evaluacion_materia', materia_id=materia.id)

        evaluacion, created = EvaluacionEstudiante.objects.update_or_create(
            estudiante=estudiante,
            materia=materia,
            defaults={'respuestas': respuestas}
        )

        messages.success(request, "Evaluación guardada correctamente.")
        return redirect('evaluacion:materias_estudiante')

    context = {
        'estudiante': estudiante,
        'materia': materia,
        'preguntas_por_categoria': preguntas_por_categoria,
    }
    return render(request, 'core/evaluacion_materia.html', context)