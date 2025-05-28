from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .info_db import obtener_db_info
from ..models import CategoriaDirectivo, PreguntaDirectivo
from django.contrib.auth.decorators import login_required

@login_required
def gestion_directivo(request):
    categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "editar_categoria":
            categoria_id = request.POST.get("categoria_id")
            nuevo_nombre = request.POST.get("nuevo_nombre", "").strip()
            preguntas = request.POST.getlist("preguntas[]")

            if not nuevo_nombre:
                messages.error(request, "El nombre de la categoría no puede estar vacío.")
            else:
                categoria = get_object_or_404(CategoriaDirectivo, id=categoria_id)
                categoria.nombre = nuevo_nombre
                categoria.save()

                categoria.preguntas.all().delete()
                for texto in preguntas:
                    texto = texto.strip()
                    if texto:
                        PreguntaDirectivo.objects.create(categoria=categoria, texto=texto)

                messages.success(request, "Categoría y preguntas actualizadas correctamente.")

        elif accion == "crear_categoria":
            nombre = request.POST.get("categoria", "").strip()  # Ajuste aquí
            preguntas = request.POST.getlist("preguntas[]")

            if not nombre:
                messages.error(request, "El nombre de la categoría no puede estar vacío.")
            elif CategoriaDirectivo.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f"La categoría '{nombre}' ya existe.")
            else:
                categoria = CategoriaDirectivo.objects.create(nombre=nombre)
                for texto in preguntas:
                    texto = texto.strip()
                    if texto:
                        PreguntaDirectivo.objects.create(categoria=categoria, texto=texto)

                messages.success(request, "Categoría y preguntas creadas correctamente.")

        elif accion == "eliminar_categoria":
            categoria_id = request.POST.get("categoria_id")
            categoria = get_object_or_404(CategoriaDirectivo, id=categoria_id)
            categoria.delete()
            messages.success(request, "Categoría eliminada correctamente.")

        return redirect(reverse('evaluacion:gestion_directivo'))

    contexto = obtener_db_info(request)

    contexto.update({
        'categorias': categorias,
    })

    return render(request, 'core/crud_directivo.html', contexto)