from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Programa
from .views_home import obtener_db_info
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

@login_required
def gestion_programa(request, programa_id=None):
    programa = None  
    
    if programa_id:  
        programa = get_object_or_404(Programa, id=programa_id)
    
    programas_list = Programa.objects.all().order_by('id')  
    paginator = Paginator(programas_list, 5)  
    page_number = request.GET.get('page')  
    programas = paginator.get_page(page_number)  

    if request.method == 'POST':
        # Capturar datos del formulario
        codigo_snies = request.POST.get('codigo_snies')
        programa_nombre = request.POST.get('programa')
        nivel_formacion = request.POST.get('nivel_formacion')
        sede = request.POST.get('sede')
        numero_semestres = request.POST.get('numero_semestres')

        if programa:  # Si existe, actualizarlo
            programa.codigo_snies = codigo_snies
            programa.programa = programa_nombre
            programa.nivel_formacion = nivel_formacion
            programa.sede = sede
            programa.numero_semestres = numero_semestres
            programa.save()
            messages.success(request, 'Programa actualizado correctamente.')
        else:  # Crear uno nuevo
            Programa.objects.create(
                codigo_snies=codigo_snies,
                programa=programa_nombre,
                nivel_formacion=nivel_formacion,
                sede=sede,
                numero_semestres=numero_semestres
            )
            messages.success(request, 'Programa creado correctamente.')

        return redirect('gestion_programa')  

    contexto = obtener_db_info(request)
    contexto.update({
        'programas': programas,
        'programa': programa,  
    })
    
    return render(request, 'core/programa.html', contexto)

@login_required
def eliminar_programa(request, programa_id):
    programa = get_object_or_404(Programa, id=programa_id)
    programa.delete()
    messages.success(request, 'Programa eliminado correctamente.')
    return redirect('gestion_programa')