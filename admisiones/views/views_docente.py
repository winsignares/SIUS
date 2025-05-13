from django.shortcuts import render, redirect, get_object_or_404 
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia, MateriaDocente, Usuario
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

def asignar_materia_docente(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias = []

    programa_id = request.GET.get('programa')
    semestre_id = request.GET.get('semestre')

    if programa_id and semestre_id:
        materias = Materia.objects.filter(fk_programa=programa_id, fk_semestre=semestre_id)


    return render(request, 'core/asignar_materia_docente.html', {
        'programas': programas,
        'semestres': semestres,
        'materias': materias,
    })

@csrf_exempt
def asignar_docente(request, materia_id):
    if request.method == 'POST':
        codigo_docente = request.POST.get('codigo_docente')
        materia = get_object_or_404(Materia, id=materia_id)

        try:
            docente = Usuario.objects.get(codigo_docente=codigo_docente, fk_rol__rol='D')
        except Usuario.DoesNotExist:
            messages.error(request, 'Docente no encontrado.')
            return redirect(f"{reverse('asignar_materia_docente')}?programa={materia.fk_programa.id}&semestre={materia.fk_semestre.id}")  # ← AQUÍ CAMBIASTE

        # Verificar si ya está asignado
        if MateriaDocente.objects.filter(docente=docente, materia=materia).exists():
            messages.warning(request, 'Este docente ya está asignado a esta materia.')
        else:
            MateriaDocente.objects.create(
                docente=docente,
                materia=materia,
                fecha_asignacion=timezone.now()
            )
            messages.success(request, 'Docente asignado correctamente.')

        return redirect(f"{reverse('asignar_materia_docente')}?programa={materia.fk_programa.id}&semestre={materia.fk_semestre.id}")  # ← Y AQUÍ TAMBIÉN CAMBIASTE

    return redirect('asignar_materia_docente')


def ver_docentes_asignados(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    docentes_asignados = MateriaDocente.objects.filter(materia=materia).select_related('docente')

    return render(request, 'core/ver_docentes_asignados.html', {
        'materia': materia,
        'docentes_asignados': docentes_asignados
    })