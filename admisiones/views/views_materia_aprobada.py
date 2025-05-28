from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia
from django.contrib.auth.models import User
from ..models import Matricula, Estudiantes, MateriaAprobada
from django.contrib import messages
from .views_home import obtener_db_info  # Importar la función para obtener la información del usuario


def materias_por_programa_semestre(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias = None

    if request.method == 'POST':
        programa_id = request.POST.get('programa')
        semestre_id = request.POST.get('semestre')
        materias = Materia.objects.filter(fk_programa_id=programa_id, fk_semestre_id=semestre_id)

    # Obtener información adicional para el contexto
    contexto = obtener_db_info(request)
    contexto.update({
        'programas': programas,
        'semestres': semestres,
        'materias': materias
    })

    return render(request, 'core/materias_por_programa_semestre.html', contexto)


def gestionar_estudiantes(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    matriculas = Matricula.objects.filter(materia=materia)
    estudiantes = [matricula.estudiante for matricula in matriculas]

    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante_id')
        estado = request.POST.get('estado')

        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)

        MateriaAprobada.objects.create(
            estudiante=estudiante,
            materia=materia,
            estado_aprobacion=estado
        )

        Matricula.objects.filter(estudiante=estudiante, materia=materia).delete()

        messages.success(request, f"Estudiante {estudiante} ha sido {'aprobado' if estado == 'aprobada' else 'reprobado'} en la materia {materia}.")
        return redirect('gestionar_estudiantes', materia_id=materia.id)

    # Obtener información adicional para el contexto
    contexto = obtener_db_info(request)

    for estudiante in estudiantes:
        try:
            user = User.objects.get(username=estudiante.estudiante)
            estudiante.nombre_completo = user.get_full_name()  
            estudiante.correo_personal = user.email  
        except User.DoesNotExist:
            estudiante.nombre_completo = "Usuario no encontrado"
            estudiante.correo_personal = "Correo no disponible"

    contexto.update({
        'materia': materia,
        'estudiantes': estudiantes
    })

    return render(request, 'core/gestionar_estudiantes.html', contexto)


def estados_estudiantes(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    registros = MateriaAprobada.objects.filter(materia=materia)
    aprobados = registros.filter(estado_aprobacion='aprobada')
    reprobados = registros.filter(estado_aprobacion='reprobada')

    # Obtener información adicional para el contexto
    contexto = obtener_db_info(request)
    contexto.update({
        'materia': materia,
        'aprobados': aprobados,
        'reprobados': reprobados
    })

    return render(request, 'core/estados_estudiantes.html', contexto)
