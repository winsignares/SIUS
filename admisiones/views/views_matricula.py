from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia, Usuario, Matricula, Prerrequisito, MateriaAprobada
from django.http import JsonResponse

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

def validar_codigo(request):
    codigo = request.GET.get('codigo')
    valido = Usuario.objects.filter(codigo_estudiante=codigo, fk_rol__rol='E').exists()
    return JsonResponse({'valido': valido})

def matricular_estudiante(request):
    if request.method == 'POST':
        codigo_estudiante = request.POST.get('codigo_estudiante')
        materias_ids = request.POST.getlist('materias')

        # Validar si el código corresponde a un usuario con rol 'E'
        estudiante = get_object_or_404(Usuario, codigo_estudiante=codigo_estudiante, fk_rol__rol='E')

        materias_a_matricular = []
        errores = []

        for materia_id in materias_ids:
            materia = get_object_or_404(Materia, id=materia_id)

            # Verificar si el estudiante ya está matriculado en la materia
            if Matricula.objects.filter(estudiante=estudiante, materia=materia).exists():
                errores.append(f'El estudiante ya está matriculado en {materia.materia}.')
            else:
                materias_a_matricular.append(materia)

        # Registrar los mensajes de error
        if errores:
            for error in errores:
                messages.warning(request, error)

        # Crear las matrículas
        if materias_a_matricular:
            for materia in materias_a_matricular:
                Matricula.objects.create(estudiante=estudiante, materia=materia)
            messages.success(request, f'Matrícula completada con éxito para {len(materias_a_matricular)} materias.')

        # Si no hay materias seleccionadas correctamente, mostrar un mensaje
        if not materias_a_matricular and errores:
            messages.error(request, 'No se pudo completar la matrícula debido a conflictos.')

        return redirect('seleccionar_programa_semestre')

    messages.error(request, 'Método no permitido.')
    return redirect('seleccionar_programa_semestre')

def validar_materias(request):
    codigo = request.GET.get('codigo')
    try:
        estudiante = Usuario.objects.get(codigo_estudiante=codigo, fk_rol__rol='E')
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Estudiante no encontrado.'}, status=400)

    materias_inscritas = list(Matricula.objects.filter(estudiante=estudiante).values_list('materia_id', flat=True))
    return JsonResponse({'materias_inscritas': materias_inscritas}, status=200)

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