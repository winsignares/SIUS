from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Pensum, Programa
from django.contrib import messages
from .views_home import obtener_db_info
from django.core.paginator import Paginator


def gestion_pensum(request, pensum_id=None):
    pensum = None  

    if pensum_id:  
        pensum = get_object_or_404(Pensum, id=pensum_id)

    pensums_list = Pensum.objects.all().order_by('id')
    paginator = Paginator(pensums_list, 5)  

    page_number = request.GET.get('page')
    pensums = paginator.get_page(page_number)

    programas = Programa.objects.all()

    if request.method == 'POST':
        id_pensum = request.POST.get('id_pensum')
        programa_id = request.POST.get('programa')
        codigo_pensum = request.POST.get('codigo_pensum')
        vigente = request.POST.get('vigente') == 'on'

        if pensum:  # Actualizar pensum existente
            pensum.fk_programa_id = programa_id
            pensum.codigo_pensum = codigo_pensum
            pensum.vigente = vigente
            pensum.save()
            messages.success(request, 'Pensum actualizado correctamente.')
        else:  # Crear nuevo pensum
            Pensum.objects.create(
                fk_programa_id=programa_id,
                codigo_pensum=codigo_pensum,
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
