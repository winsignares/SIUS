from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia, Usuario, Matricula, Prerrequisito, MateriaAprobada


def seleccionar_programa_semestre(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias = None  # Por defecto no se muestran materias

    programa_id = request.GET.get('programa')
    semestre_id = request.GET.get('semestre')

    if programa_id and semestre_id:
        materias = Materia.objects.filter(
            fk_programa_id=programa_id,
            fk_semestre_id=semestre_id
        )

    return render(request, 'core/matricular_estudiante.html', {
        'programas': programas,
        'semestres': semestres,
        'materias': materias,
        'request': request  # Para que funcione el "selected" en el template
    })

def matricular_estudiante(request):
    if request.method == 'POST':
        codigo_estudiante = request.POST.get('codigo_estudiante')
        materia_id = request.POST.get('materia_id')

        estudiante = get_object_or_404(Usuario, codigo_estudiante=codigo_estudiante, fk_rol__rol='E')
        materia = get_object_or_404(Materia, id=materia_id)

        # Obtener los prerrequisitos de la materia seleccionada
        prerrequisitos = Prerrequisito.objects.filter(materia=materia).select_related('prerequisito')

        # Verificar que todos los prerrequisitos hayan sido aprobados por el estudiante
        for prereq in prerrequisitos:
            aprobado = MateriaAprobada.objects.filter(
                estudiante=estudiante,
                materia=prereq.prerequisito,
                estado_aprobacion='aprobada'
            ).exists()

            if not aprobado:
                messages.error(
                    request,
                    f"El estudiante debe aprobar la materia '{prereq.prerequisito.materia}' antes de inscribirse en '{materia.materia}'."
                )
                return redirect('seleccionar_programa_semestre')

        # Registrar la matrícula si pasa la validación
        matricula, created = Matricula.objects.get_or_create(estudiante=estudiante, materia=materia)
        if created:
            messages.success(request, 'Estudiante matriculado exitosamente.')
        else:
            messages.info(request, 'El estudiante ya está matriculado en esta materia.')

    return redirect('seleccionar_programa_semestre')


def estudiantes_inscritos(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    matriculas = Matricula.objects.filter(materia=materia).select_related('estudiante')
    estudiantes = [matricula.estudiante for matricula in matriculas]

    context = {
        'materia': materia,
        'estudiantes': estudiantes,
    }
    return render(request, 'core/listado_estudiantes_inscritos.html', context)

def eliminar_estudiante(request, materia_id, estudiante_id):
    
    if request.method == 'POST':
        estudiante = get_object_or_404(Usuario, id=estudiante_id)
        materia = get_object_or_404(Materia, id=materia_id)
        
       
        matricula = get_object_or_404(Matricula, estudiante=estudiante, materia=materia)

    
        matricula.delete()
        
        messages.success(request, f"El estudiante {estudiante.primer_nombre} fue eliminado de la materia {materia.materia}.")
        return redirect('estudiantes_inscritos', materia_id=materia.id)
    
    return redirect('estudiantes_inscritos', materia_id=materia_id)