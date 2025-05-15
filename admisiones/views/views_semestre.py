from django.shortcuts import render, redirect, get_object_or_404
from .views_home import obtener_db_info
from home.models.carga_academica.datos_adicionales import Semestre
from django.contrib import messages

def gestion_semestre(request):
    semestres = Semestre.objects.all()
    if request.method == 'POST':
        nombre_semestre = request.POST.get('semestre')
        descripcion = request.POST.get('descripcion')
        if nombre_semestre:
            Semestre.objects.create(semestre=nombre_semestre, descripcion=descripcion)
            messages.success(request, 'Semestre creado correctamente.')
            return redirect('gestion_semestre')
        
    contexto = obtener_db_info(request)
    contexto.update({'semestres': semestres})
    
    return render(request, 'core/semestre.html', contexto)

def actualizar_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    if request.method == 'POST':
        semestre.semestre = request.POST.get('semestre')
        semestre.descripcion = request.POST.get('descripcion')
        semestre.save()
        messages.success(request, 'Semestre actualizado correctamente.')
        return redirect('gestion_semestre')
    semestres = Semestre.objects.all()
    return render(request, 'core/semestre.html', {
        'editar': True,
        'semestre': semestre,
        'semestres': semestres
    })

def eliminar_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    semestre.delete()
    messages.success(request, 'Semestre eliminado correctamente.')
    return redirect('gestion_semestre')
