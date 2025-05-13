from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Pensum, Programa
from django.contrib import messages

def gestion_pensum(request, pensum_id=None):
    pensums = Pensum.objects.all()
    programas = Programa.objects.all()
    pensum = None

    if pensum_id:
        pensum = get_object_or_404(Pensum, id=pensum_id)

    if request.method == 'POST':
        id_pensum = request.POST.get('id_pensum')
        programa_id = request.POST.get('programa')
        pensum_valor = request.POST.get('pensum')
        fecha_apertura = request.POST.get('fecha_apertura')
        fecha_cierre = request.POST.get('fecha_cierre')
        vigente = request.POST.get('vigente') == 'on'

        if id_pensum:
            pensum = get_object_or_404(Pensum, id=id_pensum)
            pensum.fk_programa_id = programa_id
            pensum.pensum = pensum_valor
            pensum.fecha_apertura = fecha_apertura or None
            pensum.fecha_cierre = fecha_cierre or None
            pensum.vigente = vigente
            pensum.save()
            messages.success(request, 'Pensum actualizado correctamente.')
        else:
            Pensum.objects.create(
                fk_programa_id=programa_id,
                pensum=pensum_valor,
                fecha_apertura=fecha_apertura or None,
                fecha_cierre=fecha_cierre or None,
                vigente=vigente
            )
            messages.success(request, 'Pensum creado correctamente.')

        return redirect('gestion_pensum')

    return render(request, 'core/pensum.html', {
        'pensums': pensums,
        'programas': programas,
        'pensum': pensum
    })

def eliminar_pensum(request, pensum_id):
    pensum = get_object_or_404(Pensum, id=pensum_id)
    pensum.delete()
    messages.success(request, 'Pensum eliminado correctamente.')
    return redirect('gestion_pensum')
