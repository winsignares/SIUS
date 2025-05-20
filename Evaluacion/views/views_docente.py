from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import CategoriaDocente, EvaluacionDocente, PreguntaDocente
from home.models.talento_humano import Usuario

@login_required
def autoevaluacion_docente(request):
    docente = request.user

    
    if not hasattr(docente, 'fk_rol') or docente.fk_rol.rol != 'D':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return render(request, 'core/error_acceso.html')  

    categorias = CategoriaDocente.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    if request.method == 'POST':
        pregunta_ids = request.POST.getlist('pregunta_id')

        evaluadas = EvaluacionDocente.objects.filter(
            docente=docente,
            pregunta_id__in=pregunta_ids
        ).values_list('pregunta_id', flat=True)

        nuevas = 0
        for pregunta_id in pregunta_ids:
            if int(pregunta_id) in evaluadas:
                continue

            respuesta = request.POST.get(f'respuesta_{pregunta_id}')
            if respuesta is not None:
                EvaluacionDocente.objects.create(
                    docente=docente,
                    pregunta_id=pregunta_id,
                    respuesta=respuesta
                )
                nuevas += 1

        if nuevas == 0:
            messages.warning(request, "Ya has realizado esta autoevaluación.")
        else:
            messages.success(request, "Autoevaluación enviada correctamente.")

    return render(request, 'core/autoevaluacion_docente.html', {
        'docente': docente,
        'preguntas_por_categoria': preguntas_por_categoria
    })