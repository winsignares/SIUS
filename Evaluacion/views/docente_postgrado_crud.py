from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Evaluacion.views.info_db import obtener_db_info
from ..models import CategoriaDocentePostgrado, PreguntaDocentePostgrado

@login_required
def gestion_docente_postgrado(request):
    categorias = CategoriaDocentePostgrado.objects.prefetch_related('preguntas').all()

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "editar_categoria":
            categoria_id = request.POST.get("categoria_id")
            nuevo_nombre = request.POST.get("nuevo_nombre", "").strip()
            preguntas = request.POST.getlist("preguntas[]")

            if not nuevo_nombre:
                messages.error(request, "El nombre de la categoría no puede estar vacío.")
            else:
                categoria = get_object_or_404(CategoriaDocentePostgrado, id=categoria_id)
                categoria.nombre = nuevo_nombre
                categoria.save()

                # Eliminar preguntas existentes y agregar las nuevas
                categoria.preguntas.all().delete()
                for texto in preguntas:
                    texto = texto.strip()
                    if texto:
                        PreguntaDocentePostgrado.objects.create(categoria=categoria, texto=texto)

                messages.success(request, "Categoría y preguntas actualizadas correctamente.")

        elif accion == "crear_categoria":
            nombre = request.POST.get("categoria", "").strip()
            preguntas = request.POST.getlist("preguntas[]")

            if not nombre:
                messages.error(request, "El nombre de la categoría no puede estar vacío.")
            elif CategoriaDocentePostgrado.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f"La categoría '{nombre}' ya existe.")
            else:
                categoria = CategoriaDocentePostgrado.objects.create(nombre=nombre)
                for texto in preguntas:
                    texto = texto.strip()
                    if texto:
                        PreguntaDocentePostgrado.objects.create(categoria=categoria, texto=texto)

                messages.success(request, "Categoría y preguntas creadas correctamente.")

        elif accion == "eliminar_categoria":
            categoria_id = request.POST.get("categoria_id")
            categoria = get_object_or_404(CategoriaDocentePostgrado, id=categoria_id)
            categoria.delete()
            messages.success(request, "Categoría eliminada correctamente.")

        return redirect(reverse('evaluacion:gestion_docente_postgrado'))

    contexto = obtener_db_info(request)
    contexto.update({
        'categorias': categorias,
    })

    return render(request, 'core/crud_docente_postgrado.html', contexto)

