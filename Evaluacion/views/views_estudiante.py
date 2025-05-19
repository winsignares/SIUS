from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Usuario, Programa, Semestre, Materia, Matricula
from ..models import PreguntaEstudiante, EvaluacionEstudiante, CategoriaEstudiante
from collections import defaultdict

def materias_estudiante_view(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    estudiantes = None
    materias = None
    estudiante = None

    programa_id = request.GET.get('programa')
    semestre_id = request.GET.get('semestre')
    estudiante_id = request.GET.get('estudiante')

    if programa_id and semestre_id:
        estudiantes = Usuario.objects.filter(
            fk_rol__rol='E',
            programa_id=programa_id,
            semestre_id=semestre_id
        )
    if estudiante_id:
        estudiante = get_object_or_404(Usuario, id=estudiante_id, fk_rol__rol="E")
        materias = Materia.objects.filter(
            matricula__estudiante=estudiante,
            fk_programa=estudiante.programa,
            fk_semestre=estudiante.semestre
        ).distinct()

    return render(request, 'core/materias_estudiante.html', {
        'programas': programas,
        'semestres': semestres,
        'estudiantes': estudiantes,
        'selected_programa': programa_id,
        'selected_semestre': semestre_id,
        'selected_estudiante': estudiante_id,
        'materias': materias,
        'estudiante': estudiante,
    })



def evaluar_materia(request, estudiante_id, materia_id):
    # Obtener estudiante y materia
    estudiante = get_object_or_404(Usuario, pk=estudiante_id)
    materia = get_object_or_404(Materia, pk=materia_id)
    
    # Obtener todas las preguntas activas agrupadas por categoría
    categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()
    
    # Agrupar preguntas activas por categoría
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        respuestas = request.POST.getlist('respuesta')
        pregunta_ids = request.POST.getlist('pregunta_id')

        for pregunta_id, respuesta in zip(pregunta_ids, respuestas):
            EvaluacionEstudiante.objects.create(
                estudiante=estudiante,
                materia=materia,
                pregunta_id=pregunta_id,
                respuesta=respuesta
            )
        return redirect('evaluacion:materias_estudiante')

    context = {
        'estudiante': estudiante,
        'materia': materia,
        'preguntas_por_categoria': preguntas_por_categoria,
    }
    return render(request, 'core/evaluacion_materia.html', context)