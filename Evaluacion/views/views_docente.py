from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import CategoriaDocente, EvaluacionDocente, PreguntaDocente
from home.models.talento_humano import Usuario

@login_required
def autoevaluacion_docente(request):
    usuario = request.user  

    categorias = CategoriaDocente.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        pregunta_ids = request.POST.getlist('pregunta_id')

        evaluaciones_existentes = EvaluacionDocente.objects.filter(
            docente=usuario,
            pregunta_id__in=pregunta_ids
        ).values_list('pregunta_id', flat=True)

        nuevas_evaluaciones = 0

        for pregunta_id in pregunta_ids:
            if int(pregunta_id) in evaluaciones_existentes:
                continue

            respuesta = request.POST.get(f'respuesta_{pregunta_id}')
            if respuesta is not None:
                EvaluacionDocente.objects.create(
                    docente=usuario,
                    pregunta_id=pregunta_id,
                    respuesta=respuesta
                )
                nuevas_evaluaciones += 1

        if nuevas_evaluaciones == 0:
            messages.warning(request, "Ya realizaste esta autoevaluación anteriormente.")
        else:
            messages.success(request, "Autoevaluación registrada correctamente.")

        return redirect('evaluacion:autoevaluacion_docente')

    context = {
        'docente': usuario,
        'preguntas_por_categoria': preguntas_por_categoria,
    }
    return render(request, 'core/autoevaluacion_docente.html', context)