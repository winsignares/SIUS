from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from ..models import CategoriaDocente, PreguntaDocente
from django.http import HttpResponse

def gestion_docente(request):
    categorias = CategoriaDocente.objects.prefetch_related('preguntas').all()

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "editar_pregunta":
            pregunta_id = request.POST.get("pregunta_id")
            nuevo_texto = request.POST.get("nuevo_texto", "").strip()
            if not nuevo_texto:
                messages.error(request, "El texto de la pregunta no puede estar vacío.")
            else:
                pregunta = get_object_or_404(PreguntaDocente, id=pregunta_id)
                pregunta.texto = nuevo_texto
                pregunta.save()
                messages.success(request, "Pregunta actualizada correctamente.")

        elif accion == "eliminar_pregunta":
            pregunta_id = request.POST.get("pregunta_id")
            pregunta = get_object_or_404(PreguntaDocente, id=pregunta_id)
            pregunta.delete()
            messages.success(request, "Pregunta eliminada correctamente.")

        elif accion == "editar_categoria":
            categoria_id = request.POST.get("categoria_id")
            nuevo_nombre = request.POST.get("nuevo_nombre", "").strip()
            if not nuevo_nombre:
                messages.error(request, "El nombre de la categoría no puede estar vacío.")
            else:
                categoria = get_object_or_404(CategoriaDocente, id=categoria_id)
                categoria.nombre = nuevo_nombre
                categoria.save()
                messages.success(request, "Categoría actualizada correctamente.")

        elif accion == "eliminar_categoria":
            categoria_id = request.POST.get("categoria_id")
            categoria = get_object_or_404(CategoriaDocente, id=categoria_id)
            categoria.delete()
            messages.success(request, "Categoría eliminada correctamente.")

        elif accion == "crear_categoria":
            nombre = request.POST.get("categoria", "").strip()
            if not nombre:
                messages.error(request, "El nombre de la categoría no puede estar vacío.")
            elif CategoriaDocente.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f"La categoría '{nombre}' ya existe.")
            else:
                CategoriaDocente.objects.create(nombre=nombre)
                messages.success(request, "Categoría creada correctamente.")

        elif accion == "crear_preguntas":
            categoria_id = request.POST.get("categoria_id")
            preguntas = request.POST.getlist("preguntas[]")
            categoria = get_object_or_404(CategoriaDocente, id=categoria_id)
            for texto in preguntas:
                texto = texto.strip()
                if texto:
                    PreguntaDocente.objects.create(categoria=categoria, texto=texto)
            messages.success(request, "Preguntas creadas correctamente.")

        return redirect(reverse('evaluacion:gestion_docente'))

    return render(request, 'core/crud_docente.html', {'categorias': categorias})
