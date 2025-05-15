from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Materia, Pensum, Semestre, Programa
from django.contrib import messages
from .views_home import obtener_db_info

def gestion_materia(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    pensums = Pensum.objects.all()
    materias = Materia.objects.all()

    if request.method == 'POST':
        materia_nombre = request.POST.get('materia')
        codigo = request.POST.get('codigo')
        creditos = request.POST.get('creditos')
        metodologia = request.POST.get('metodologia')
        horas = request.POST.get('horas')
        programa_id = request.POST.get('programa')
        pensum_id = request.POST.get('pensum')
        semestre_id = request.POST.get('semestre')

    

        if all([materia_nombre, codigo, creditos, programa_id, pensum_id, semestre_id]):
            Materia.objects.create(
                materia=materia_nombre,
                codigo=codigo,
                creditos=creditos,
                metodologia=metodologia,
                horas=horas,
                fk_programa_id=programa_id,
                fk_pensum_id=pensum_id,
                fk_semestre_id=semestre_id
            )
            messages.success(request, 'Materia registrada correctamente.')
            return redirect('gestion_materia')
        else:
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')

    if request.GET.get('programa') or request.GET.get('semestre'):
        if request.GET.get('programa'):
            materias = materias.filter(fk_programa_id=request.GET['programa'])
        if request.GET.get('semestre'):
            materias = materias.filter(fk_semestre_id=request.GET['semestre'])

    contexto = obtener_db_info(request)
    contexto.update({
        'programas': programas,
        'semestres': semestres,
        'pensums': pensums,
        'materias': materias
    })
    
    return render(request, 'core/materia.html', contexto)


def actualizar_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    programas = Programa.objects.all()
    pensums = Pensum.objects.all()
    semestres = Semestre.objects.all()

    if request.method == 'POST':
        materia_nombre = request.POST.get('materia')
        codigo = request.POST.get('codigo')
        creditos = request.POST.get('creditos')
        metodologia = request.POST.get('metodologia')
        horas = request.POST.get('horas')
        programa_id = request.POST.get('programa')
        pensum_id = request.POST.get('pensum')
        semestre_id = request.POST.get('semestre')



        if all([materia_nombre, codigo, creditos, programa_id, pensum_id, semestre_id]):
            materia.materia = materia_nombre
            materia.codigo = codigo
            materia.creditos = creditos
            materia.metodologia = metodologia
            materia.horas = horas
            materia.fk_programa_id = programa_id
            materia.fk_pensum_id = pensum_id
            materia.fk_semestre_id = semestre_id
            materia.save()
            messages.success(request, 'Materia actualizada correctamente.')
            return redirect('gestion_materia')
        else:
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')

    return render(request, 'core/materia.html', {
        'editar': True,
        'materia_obj': materia,
        'programas': programas,
        'pensums': pensums,
        'semestres': semestres
    })


def eliminar_materia(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    materia.delete()
    messages.success(request, 'Materia eliminada correctamente.')
    return redirect('gestion_materia')
