from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from Evaluacion.views.info_db import obtener_db_info
from ..models import CategoriaEstudiante, PreguntaEstudiante
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def gestion_estudiantes(request):
    from ..models import CategoriaEstudiante, PreguntaEstudiante

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear_categoria':
            nombre = request.POST.get('categoria')
            if nombre:
                CategoriaEstudiante.objects.create(nombre=nombre)
                messages.success(request, "Categoría creada correctamente.")
            else:
                messages.error(request, "Debe ingresar un nombre para la categoría.")

        elif accion == 'editar_categoria':
            categoria_id = request.POST.get('categoria_id')
            nuevo_nombre = request.POST.get('nuevo_nombre')
            if categoria_id and nuevo_nombre:
                categoria = get_object_or_404(CategoriaEstudiante, id=categoria_id)
                categoria.nombre = nuevo_nombre
                categoria.save()
                messages.success(request, "Categoría actualizada correctamente.")

        elif accion == 'eliminar_categoria':
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                categoria = get_object_or_404(CategoriaEstudiante, id=categoria_id)
                categoria.delete()
                messages.success(request, "Categoría eliminada correctamente.")

        elif accion == 'crear_preguntas':
            categoria_id = request.POST.get('categoria_id')
            preguntas = request.POST.getlist('preguntas[]')
            if categoria_id and preguntas:
                categoria = get_object_or_404(CategoriaEstudiante, id=categoria_id)
                for texto in preguntas:
                    if texto.strip():
                        PreguntaEstudiante.objects.create(categoria=categoria, texto=texto.strip())
                messages.success(request, f"Preguntas creadas para la categoría {categoria.nombre}.")

        elif accion == 'editar_pregunta':
            pregunta_id = request.POST.get('pregunta_id')
            nuevo_texto = request.POST.get('nuevo_texto')
            if pregunta_id and nuevo_texto:
                pregunta = get_object_or_404(PreguntaEstudiante, id=pregunta_id)
                pregunta.texto = nuevo_texto
                pregunta.save()
                messages.success(request, "Pregunta actualizada correctamente.")

        elif accion == 'eliminar_pregunta':
            pregunta_id = request.POST.get('pregunta_id')
            if pregunta_id:
                pregunta = get_object_or_404(PreguntaEstudiante, id=pregunta_id)
                pregunta.delete()
                messages.success(request, "Pregunta eliminada correctamente.")

        return redirect('evaluacion:gestion_estudiantes')  # Ajusta el nombre de tu URL aquí

    categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()

    contexto = obtener_db_info(request)

    contexto.update({
        'categorias': categorias,
    })
    return render(request, 'core/crud_estudiante.html', contexto)
