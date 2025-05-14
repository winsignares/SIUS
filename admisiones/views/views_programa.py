from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Programa
from django.contrib import messages
def gestion_programa(request, programa_id=None):
    programas = Programa.objects.all()
    programa = None

    if programa_id:
        programa = get_object_or_404(Programa, id=programa_id)

    if request.method == 'POST':
       
        codigo_snies = request.POST.get('codigo_snies')
        programa_nombre = request.POST.get('programa')
        nivel_formacion = request.POST.get('nivel_formacion')
        sede = request.POST.get('sede')
        numero_semestres = request.POST.get('numero_semestres')
        id_programa = request.POST.get('id_programa')

        if id_programa:
            programa = get_object_or_404(Programa, id=id_programa)
            programa.codigo_snies = codigo_snies  # Guardamos el código SNIES
            programa.programa = programa_nombre
            programa.nivel_formacion = nivel_formacion
            programa.sede = sede
            programa.numero_semestres = numero_semestres
            programa.save()
            messages.success(request, 'Programa actualizado correctamente.')
        else:
            Programa.objects.create(codigo_snies=codigo_snies, programa=programa_nombre, nivel_formacion=nivel_formacion,
                                    sede=sede, numero_semestres=numero_semestres)
            messages.success(request, 'Programa creado correctamente.')

        return redirect('gestion_programa')

    return render(request, 'core/programa.html', {
        'programas': programas,
        'programa': programa
    })
def eliminar_programa(request, programa_id):
    programa = get_object_or_404(Programa, id=programa_id)
    programa.delete()
    messages.success(request, 'Programa eliminado correctamente.')
    return redirect('gestion_programa')