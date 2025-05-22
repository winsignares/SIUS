# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import CategoriaDirectivo, PreguntaDirectivo, EvaluacionDirectivo
from home.models.talento_humano.usuarios import Usuario
from django.contrib.auth.models import User

@login_required
def listado_docentes(request):
    docentes = Usuario.objects.filter(fk_rol__rol='D', activo=True)
    return render(request, 'core/listado_docentes.html', {'docentes': docentes})

@login_required
def evaluar_docente(request, docente_id):
    docente_evaluado = get_object_or_404(Usuario, id=docente_id)

    categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        pregunta_ids = request.POST.getlist('pregunta_id')
        evaluador = request.user

        evaluaciones_existentes = EvaluacionDirectivo.objects.filter(
            evaluador=evaluador,
            docente_evaluado=docente_evaluado,
            pregunta_id__in=pregunta_ids
        ).values_list('pregunta_id', flat=True)

        nuevas_evaluaciones = 0

        for pregunta_id in pregunta_ids:
            if int(pregunta_id) in evaluaciones_existentes:
                continue

            respuesta = request.POST.get(f'respuesta_{pregunta_id}')
            if respuesta is not None:
                EvaluacionDirectivo.objects.create(
                    evaluador=evaluador,
                    docente_evaluado=docente_evaluado,
                    pregunta_id=pregunta_id,
                    respuesta=respuesta
                )
                nuevas_evaluaciones += 1

        if nuevas_evaluaciones == 0:
            messages.warning(request, "Ya realizaste esta evaluación anteriormente.")
        else:
            messages.success(request, "Evaluación registrada correctamente.")

        return redirect('evaluacion:listado_docentes')

    context = {
        'docente': docente_evaluado,
        'preguntas_por_categoria': preguntas_por_categoria,
    }
    return render(request, 'core/evaluar_docente.html', context)
