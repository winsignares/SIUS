from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from ..models import CategoriaEstudiante, PreguntaEstudiante, CategoriaDocente, PreguntaDocente, CategoriaDirectivo, PreguntaDirectivo
from django.http import HttpResponse
# Función auxiliar para obtener preguntas según el rol
def obtener_pregunta_por_rol(rol, pregunta_id):
    modelos = {
        'E': PreguntaEstudiante,
        'D': PreguntaDocente,
        'DR': PreguntaDirectivo,
    }
    modelo = modelos.get(rol)
    if modelo:
        return get_object_or_404(modelo, id=pregunta_id)
    return None

def obtener_categoria_por_rol(rol, categoria_id):
    modelos = {
        'E': CategoriaEstudiante,
        'D': CategoriaDocente,
        'DR': CategoriaDirectivo,
    }
    modelo = modelos.get(rol)
    if modelo:
        return get_object_or_404(modelo, id=categoria_id)
    return None


def editar_categoria(request):
    if request.method == 'POST':
        categoria_id = request.POST.get("categoria_id")
        nuevo_nombre = request.POST.get("nuevo_nombre", "").strip()
        rol = request.POST.get("rol")

        if not nuevo_nombre:
            messages.error(request, "El nombre de la categoría no puede estar vacío.")
        else:
            categoria = obtener_categoria_por_rol(rol, categoria_id)
            if categoria:
                categoria.nombre = nuevo_nombre
                
                categoria.save()
                messages.success(request, "Categoría actualizada correctamente.")
            else:
                messages.error(request, "Categoría no encontrada.")

        return redirect(f"{reverse('evaluacion:gestion_roles')}?rol={rol}")

    return HttpResponse("Método no permitido", status=405)


def eliminar_categoria(request):
    if request.method == 'POST':
        categoria_id = request.POST.get("categoria_id")
        rol = request.POST.get("rol")

        categoria = obtener_categoria_por_rol(rol, categoria_id)
        if categoria:
            categoria.delete()
            messages.success(request, "Categoría eliminada correctamente.")
        else:
            messages.error(request, "No se pudo encontrar la categoría.")

        return redirect(f"{reverse('evaluacion:gestion_roles')}?rol={rol}")

    return HttpResponse("Método no permitido", status=405)

def gestion_roles(request):
    rol = request.POST.get('rol') or request.GET.get('rol')
    categorias = []

    # Cargar categorías según el rol
    if rol == 'E':
        categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()
    elif rol == 'D':
        categorias = CategoriaDocente.objects.prefetch_related('preguntas').all()
    elif rol == 'DR':
        categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()

    if request.method == "POST":
        accion = request.POST.get("accion")
        pregunta_id = request.POST.get("pregunta_id")

        # Editar Pregunta
        if accion == "editar":
            nuevo_texto = request.POST.get("nuevo_texto", "").strip()
            if not nuevo_texto:
                messages.error(request, "El texto de la pregunta no puede estar vacío.")
            else:
                pregunta = obtener_pregunta_por_rol(rol, pregunta_id)
                if pregunta:
                    pregunta.texto = nuevo_texto
                    pregunta.save()
                    messages.success(request, "Pregunta actualizada correctamente.")
                else:
                    messages.error(request, "No se pudo encontrar la pregunta.")

        # Eliminar Pregunta
        elif accion == "eliminar":
            pregunta = obtener_pregunta_por_rol(rol, pregunta_id)
            if pregunta:
                pregunta.delete()
                messages.success(request, "Pregunta eliminada correctamente.")
            else:
                messages.error(request, "No se pudo encontrar la pregunta para eliminar.")

        # Redirigir manteniendo el rol seleccionado
        return redirect(f"{reverse('evaluacion:gestion_roles')}?rol={rol}")

    # Renderizar la plantilla
    return render(request, 'core/crud_evaluacion.html', {'rol': rol, 'categorias': categorias})

def crear_categoria(request):
    if request.method == 'POST':
        rol = request.POST.get('rol')
        nombre = request.POST.get('categoria')
       

        if rol == 'E':
            CategoriaEstudiante.objects.create(nombre=nombre)
        elif rol == 'D':
            CategoriaDocente.objects.create(nombre=nombre)
        elif rol == 'DR':
            CategoriaDirectivo.objects.create(nombre=nombre)

        return redirect(f"{reverse('evaluacion:gestion_roles')}?rol={rol}")

def crear_pregunta(request):
    if request.method == 'POST':
        rol = request.POST.get('rol')
        categoria_id = request.POST.get('categoria_id')
        texto = request.POST.get('pregunta')

        if rol == 'E':
            categoria = CategoriaEstudiante.objects.get(id=categoria_id)
            PreguntaEstudiante.objects.create(categoria=categoria, texto=texto)
        elif rol == 'D':
            categoria = CategoriaDocente.objects.get(id=categoria_id)
            PreguntaDocente.objects.create(categoria=categoria, texto=texto)
        elif rol == 'DR':
            categoria = CategoriaDirectivo.objects.get(id=categoria_id)
            PreguntaDirectivo.objects.create(categoria=categoria, texto=texto)

        return redirect(f"{reverse('evaluacion:gestion_roles')}?rol={rol}")
    

def editar_pregunta(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        pregunta_id = request.POST.get('pregunta_id')
        nuevo_texto = request.POST.get('nuevo_texto')
        rol = request.POST.get('rol')

        # Validar que el texto no esté vacío
        if not nuevo_texto.strip():
            messages.error(request, "El texto de la pregunta no puede estar vacío.")
            return redirect(f"{reverse('gestion_roles')}?rol={rol}")

        # Obtener la pregunta según el rol y la categoría
        pregunta = None
        if rol == 'E':
            pregunta = get_object_or_404(PreguntaEstudiante, id=pregunta_id)
        elif rol == 'D':
            pregunta = get_object_or_404(PreguntaDocente, id=pregunta_id)
        elif rol == 'DR':
            pregunta = get_object_or_404(PreguntaDirectivo, id=pregunta_id)
        else:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('gestion_roles')

        # Actualizar el texto de la pregunta
        pregunta.texto = nuevo_texto
        pregunta.save()
        messages.success(request, "La pregunta ha sido actualizada correctamente.")
        return redirect(f"{reverse('evaluacion:gestion_roles')}?rol={rol}")

    return HttpResponse("Método no permitido", status=405)