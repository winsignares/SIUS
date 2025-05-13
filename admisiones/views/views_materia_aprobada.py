# views_materia_aprobada.py
from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales  import MateriaAprobada, Usuario, Programa, Semestre, Materia, Matricula
from django.contrib import messages


def materias_por_programa_semestre(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias = None

    if request.method == 'POST':
        programa_id = request.POST.get('programa')
        semestre_id = request.POST.get('semestre')
        materias = Materia.objects.filter(fk_programa_id=programa_id, fk_semestre_id=semestre_id)

    return render(request, 'core/materias_por_programa_semestre.html', {
        'programas': programas,
        'semestres': semestres,
        'materias': materias
    })

def gestionar_estudiantes(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    matriculas = Matricula.objects.filter(materia=materia)
    estudiantes = [matricula.estudiante for matricula in matriculas]

    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante_id')
        estado = request.POST.get('estado')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_finalizacion = request.POST.get('fecha_finalizacion')

        estudiante = get_object_or_404(Usuario, id=estudiante_id)

       
        MateriaAprobada.objects.create(
            estudiante=estudiante,
            materia=materia,
            fecha_inicio=fecha_inicio,
            fecha_finalizacion=fecha_finalizacion,
            estado_aprobacion=estado
        )

      
        Matricula.objects.filter(estudiante=estudiante, materia=materia).delete()

        messages.success(request, f"Estudiante {estudiante} ha sido {'aprobado' if estado == 'aprobada' else 'reprobado'} en la materia {materia}.")
        return redirect('gestionar_estudiantes', materia_id=materia.id)

    return render(request, 'core/gestionar_estudiantes.html', {
        'materia': materia,
        'estudiantes': estudiantes
    })

def estados_estudiantes(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    registros = MateriaAprobada.objects.filter(materia=materia)
    aprobados = registros.filter(estado_aprobacion='aprobada')
    reprobados = registros.filter(estado_aprobacion='reprobada')

    return render(request, 'core/estados_estudiantes.html', {
        'materia': materia,
        'aprobados': aprobados,
        'reprobados': reprobados
    })