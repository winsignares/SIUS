from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .views_home import obtener_db_info
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia
from ..models import Estudiantes, Matricula
from django.http import JsonResponse


def seleccionar_programa_semestre(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias = None  
    estudiantes = []  

    programa_id = request.GET.get('programa')
    semestre_id = request.GET.get('semestre')

    if programa_id and semestre_id:
        
        materias = Materia.objects.filter(
            fk_programa_id=programa_id,
            fk_semestre_id=semestre_id
        )

        
        estudiantes = Estudiantes.objects.filter(
            programa_id=programa_id, 
            semestre_id=semestre_id   
        )

    contexto = obtener_db_info(request)
    contexto.update({
        'programas': programas,
        'semestres': semestres,
        'materias': materias,
        'estudiantes': estudiantes,  
        'request': request  
    })

    return render(request, 'core/matricular_estudiantes.html', contexto)


def filtrar_estudiantes(request):
    programa_id = request.GET.get('programa')
    semestre_id = request.GET.get('semestre')

    if not programa_id or not semestre_id:
        return JsonResponse({"error": "Faltan parámetros"}, status=400)

    try:
        programa_id = int(programa_id)
        semestre_id = int(semestre_id)

        programa = get_object_or_404(Programa, id=programa_id)
        semestre = get_object_or_404(Semestre, id=semestre_id)

        estudiantes = Estudiantes.objects.filter(
            programa=programa,
            semestre=semestre
        )

        estudiantes_data = [
            {
                "numero_documento": estudiante.numero_documento,
                "nombre_completo": estudiante.nombre_completo
            }
            for estudiante in estudiantes
        ]

        return JsonResponse({"estudiantes": estudiantes_data}, status=200)

    except ValueError:
        return JsonResponse({"error": "Parámetros inválidos"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)

def validar_codigo(request):
    codigo = request.GET.get('numero_documento')
    valido = Estudiantes.objects.filter(numero_documento=codigo).exists()
    return JsonResponse({'valido': valido})



def matricular_estudiante(request):
    if request.method == 'POST':
        identificacion = request.POST.get('numero_documento')
        materias_ids = request.POST.getlist('materias')

        # Validación inicial del código del estudiante
        if not identificacion :
            messages.error(request, 'Código de estudiante no proporcionado.')
            return redirect('seleccionar_programa_semestre')

        try:
            estudiante = Estudiantes.objects.get(
                numero_documento=identificacion,
            )
        except Estudiantes.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado o no tiene rol de estudiante.')
            return redirect('seleccionar_programa_semestre')

        # Validar que el estudiante tenga programa y semestre asignados
        if not estudiante.programa or not estudiante.semestre:
            messages.error(request, 'El estudiante no tiene asignado un programa o semestre.')
            return redirect('seleccionar_programa_semestre')

        materias_a_matricular = []
        errores = []

        # Evitar duplicación de matrícula
        materias_matriculadas = Matricula.objects.filter(estudiante=estudiante).values_list('materia_id', flat=True)

        for materia_id in materias_ids:
            try:
                materia = Materia.objects.get(id=materia_id)
                if materia.id in materias_matriculadas:
                    errores.append(f'Ya está matriculado en {materia.materia}.')
                else:
                    materias_a_matricular.append(materia)
            except Materia.DoesNotExist:
                errores.append(f'La materia con ID {materia_id} no existe.')

        # Mostrar errores si existen
        for error in errores:
            messages.warning(request, error)

        # Guardar matrícula si hay materias válidas
        if materias_a_matricular:
            for materia in materias_a_matricular:
                Matricula.objects.create(estudiante=estudiante, materia=materia)
            messages.success(request, f'Matrícula completada con éxito para {len(materias_a_matricular)} materias.')
        elif not materias_a_matricular:
            messages.error(request, 'No se pudo completar la matrícula. Verifique las materias seleccionadas.')

        return redirect('seleccionar_programa_semestre')

    messages.error(request, 'Método no permitido.')
    return redirect('seleccionar_programa_semestre')

def validar_materias(request):
    codigo = request.GET.get('codigo')
    try:
        estudiante = Estudiantes.objects.get(codigo_estudiante=codigo, fk_rol__rol='E')
    except Estudiantes.DoesNotExist:
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
        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)
        materia = get_object_or_404(Materia, id=materia_id)
        
       
        matricula = get_object_or_404(Matricula, estudiante=estudiante, materia=materia)

    
        matricula.delete()
        
        messages.success(request, f"El estudiante  {estudiante.nombre_completo} con una identificación: {estudiante.numero_documento},fue eliminado de la materia {materia.materia}.")
        return redirect('estudiantes_inscritos', materia_id=materia.id)
    
    return redirect('estudiantes_inscritos', materia_id=materia_id)