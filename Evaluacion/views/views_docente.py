from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import CategoriaDocente, EvaluacionDocente
from django.contrib.auth.models import User

@login_required
def autoevaluacion_docente(request):
    usuario = request.user

    categorias = CategoriaDocente.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    # Verificamos si ya existe autoevaluación para este docente
    ya_evaluado = EvaluacionDocente.objects.filter(docente=usuario).exists()

    if request.method == 'POST':
        if ya_evaluado:
            messages.warning(request, "Ya realizaste esta autoevaluación anteriormente.")
            return redirect('evaluacion:autoevaluacion_docente')

        # Obtenemos las respuestas del POST, solo las que empiezan con 'respuesta_'
        respuestas = {}
        for key, value in request.POST.items():
            if key.startswith('respuesta_'):
                pregunta_id = key.replace('respuesta_', '')
                respuestas[pregunta_id] = int(value)  # Convertimos la respuesta a int

        if not respuestas:
            messages.error(request, "No se registraron evaluaciones.")
            return redirect('evaluacion:autoevaluacion_docente')

        # Guardamos las respuestas como JSON en un solo registro
        EvaluacionDocente.objects.create(
            docente=usuario,
            respuestas=respuestas
        )

        messages.success(request, "Autoevaluación registrada correctamente.")
        return redirect('evaluacion:autoevaluacion_docente')

    context = {
        'docente': usuario,
        'preguntas_por_categoria': preguntas_por_categoria,
        'ya_evaluado': ya_evaluado,
    }
    return render(request, 'core/autoevaluacion_docente.html', context)