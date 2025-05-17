from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Pensum, Programa
from django.contrib import messages
from .views_home import obtener_db_info

def gestion_pensum(request, pensum_id=None):
    pensums = Pensum.objects.all()
    programas = Programa.objects.all()
    pensum = None
    id_pensum = None  # Inicializamos la variable

    if pensum_id:
        pensum = get_object_or_404(Pensum, id=pensum_id)

    if request.method == 'POST':
        id_pensum = request.POST.get('id_pensum')
        programa_id = request.POST.get('programa')
        pensum_valor = request.POST.get('codigo_pensum')  # Asegúrate que este nombre coincide en tu formulario HTML
        vigente = request.POST.get('vigente') == 'on'

        if id_pensum:
            pensum = get_object_or_404(Pensum, id=id_pensum)
            pensum.fk_programa_id = programa_id
            pensum.codigo_pensum = pensum_valor
            pensum.vigente = vigente
            pensum.save()
            messages.success(request, 'Pensum actualizado correctamente.')
        else:
            Pensum.objects.create(
                fk_programa_id=programa_id,
                codigo_pensum=pensum_valor,  # Campo corregido
                vigente=vigente
            )
            messages.success(request, 'Pensum creado correctamente.')

        return redirect('gestion_pensum')

    contexto = obtener_db_info(request)
    contexto.update({
        'pensums': pensums,
        'programas': programas,
        'pensum': pensum
    })

    return render(request, 'core/pensum.html', contexto)

def eliminar_pensum(request, pensum_id):
    pensum = get_object_or_404(Pensum, id=pensum_id)
    pensum.delete()
    messages.success(request, 'Pensum eliminado correctamente.')
    return redirect('gestion_pensum')
