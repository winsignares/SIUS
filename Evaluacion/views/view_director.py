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
    evaluador = request.user

    categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    # Comprobar si ya existe evaluación previa de este evaluador para este docente
    evaluacion_existente = EvaluacionDirectivo.objects.filter(
        evaluador=evaluador,
        docente_evaluado=docente_evaluado
    ).first()

    if request.method == 'POST':
        if evaluacion_existente:
            messages.warning(request, "Ya realizaste esta evaluación anteriormente.")
            return redirect('evaluacion:listado_docentes')

        respuestas = {}
        for categoria, preguntas in preguntas_por_categoria.items():
            for pregunta in preguntas:
                respuesta = request.POST.get(f'respuesta_{pregunta.id}')
                if respuesta is not None:
                    respuestas[str(pregunta.id)] = int(respuesta)

        if not respuestas:
            messages.error(request, "No se registraron evaluaciones.")
            return redirect('evaluacion:listado_docentes')

        EvaluacionDirectivo.objects.create(
            evaluador=evaluador,
            docente_evaluado=docente_evaluado,
            respuestas=respuestas
        )
        messages.success(request, "Evaluación registrada correctamente.")
        return redirect('evaluacion:listado_docentes')

    context = {
        'docente': docente_evaluado,
        'preguntas_por_categoria': preguntas_por_categoria,
        'evaluacion_existente': evaluacion_existente,
    }
    return render(request, 'core/evaluar_docente.html', context)