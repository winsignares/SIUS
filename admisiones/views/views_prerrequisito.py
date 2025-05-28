from django.shortcuts import render, redirect, get_object_or_404
from .views_home import obtener_db_info
from home.models.carga_academica.datos_adicionales import Materia, Programa, Semestre
from ..models import Prerrequisito
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
def gestion_prerrequisito(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias_filtradas = []
    materias_prerrequisito = []
    prerrequisitos = Prerrequisito.objects.none()

    if request.method == 'POST':
        programa_id = request.POST.get('programa')
        semestre_id = request.POST.get('semestre')
        materia_id = request.POST.get('materia')
        prereq_id = request.POST.get('prerrequisito')

        if materia_id and prereq_id and materia_id != prereq_id:
            Prerrequisito.objects.get_or_create(
                materia_id=materia_id,
                prerequisito_id=prereq_id
            )
            messages.success(request, "Prerrequisito asignado correctamente.")
            return redirect(f'{request.path}?programa={programa_id}&semestre={semestre_id}')
        else:
            messages.error(request, "Error al asignar prerrequisito.")
    else:
        programa_id = request.GET.get('programa')
        semestre_id = request.GET.get('semestre')

    bloquear_filtro = False
    if semestre_id:
        semestre = Semestre.objects.filter(id=semestre_id).first()
        if semestre and semestre.semestre.strip() == "1":
            messages.error(request, "No se puede filtrar para el semestre 1.")
            bloquear_filtro = True

    if programa_id and semestre_id and not bloquear_filtro:
        materias_filtradas = Materia.objects.filter(fk_programa_id=programa_id, fk_semestre_id=semestre_id)
        materias_prerrequisito = Materia.objects.filter(fk_programa_id=programa_id)
        prerrequisitos = Prerrequisito.objects.select_related('materia', 'prerequisito') \
            .filter(materia__fk_programa_id=programa_id, materia__fk_semestre_id=semestre_id)

    contexto = obtener_db_info(request)
    contexto.update({
        'programas': programas,
        'semestres': semestres,
        'materias_filtradas': materias_filtradas,
        'materias_prerrequisito': materias_prerrequisito,
        'prerrequisitos': prerrequisitos
    })

    return render(request, 'core/prerrequisito.html', contexto)

@login_required
@require_POST
def editar_prerrequisito(request, pk):
    prerrequisito = get_object_or_404(Prerrequisito, pk=pk)
    nuevo_prereq_id = request.POST.get('prerrequisito')

    if nuevo_prereq_id and str(prerrequisito.materia.id) != nuevo_prereq_id:
        prerrequisito.prerequisito_id = nuevo_prereq_id
        prerrequisito.save()
        messages.success(request, "Prerrequisito actualizado correctamente.")
    else:
        messages.error(request, "Error: No se puede asignar la misma materia como su propio prerrequisito.")

    return redirect('gestion_prerrequisito')

@login_required
def eliminar_prerrequisito(request, pk):
    prerrequisito = get_object_or_404(Prerrequisito, pk=pk)
    prerrequisito.delete()
    messages.success(request, "Prerrequisito eliminado.")
    return redirect('gestion_prerrequisito')