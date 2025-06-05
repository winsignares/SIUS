from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Count
from Evaluacion.models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from home.models.carga_academica.datos_adicionales import Periodo, Programa
from home.models.carga_academica.carga_academica import CargaAcademica
from Evaluacion.views.info_db import obtener_db_info
import json

@login_required
def graficos_por_programa(request):
    def extraer_valores_numericos(respuestas):
        valores = []
        for v in respuestas.values():
            try:
                valores.append(float(v))
            except (ValueError, TypeError):
                continue
        return valores

    contexto = obtener_db_info(request)
    contexto['programas'] = Programa.objects.all().order_by('programa')

    programa_id = request.GET.get('programa_id')
    if not programa_id:
        return render(request, 'core/graficos_por_programa.html', contexto)

    try:
        programa = Programa.objects.get(id=programa_id)
    except Programa.DoesNotExist:
        contexto['mensaje_error'] = "Programa no encontrado."
        return render(request, 'core/graficos_por_programa.html', contexto)

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).order_by('-fecha_apertura').first()

    if not periodo_activo:
        contexto['mensaje_error'] = "No hay un periodo activo configurado."
        return render(request, 'core/graficos_por_programa.html', contexto)

    cargas = CargaAcademica.objects.filter(fk_programa=programa).select_related('fk_docente_asignado')
    docentes_programa = {c.fk_docente_asignado for c in cargas if c.fk_docente_asignado}

    if not docentes_programa:
        contexto['mensaje_advertencia'] = "No hay docentes disponibles con carga académica en este programa."
        return render(request, 'core/graficos_por_programa.html', contexto)

    # Gráfico 1: Conteo de evaluadores
    evaluaciones_estudiantes_count = EvaluacionEstudiante.objects.filter(
        periodo=periodo_activo,
        materia__fk_programa=programa
    ).values('estudiante').distinct().count()

    evaluaciones_docentes_count = EvaluacionDocente.objects.filter(
        periodo=periodo_activo,
        docente__in=docentes_programa
    ).count()

    # Gráfico 2: Evaluaciones por semestre
    evaluaciones_por_semestre = EvaluacionEstudiante.objects.filter(
        periodo=periodo_activo,
        materia__fk_programa=programa
    ).values('estudiante__semestre__descripcion').annotate(
        total=Count('estudiante')
    ).order_by('estudiante__semestre__descripcion')

    semestres_data = {
        'labels': [],
        'data': [],
        'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
    }
    for item in evaluaciones_por_semestre:
        semestres_data['labels'].append(item['estudiante__semestre__descripcion'])
        semestres_data['data'].append(item['total'])

    # Gráfico 3 y 4: Promedios ponderados (top 10)
    ponderados_data = {'labels': [], 'data': []}
    for docente in docentes_programa:
        promedios = []

        est = EvaluacionEstudiante.objects.filter(
            periodo=periodo_activo,
            docente_evaluado=docente,
            materia__fk_programa=programa
        )
        auto = EvaluacionDocente.objects.filter(periodo=periodo_activo, docente=docente)
        directivo = EvaluacionDirectivo.objects.filter(periodo=periodo_activo, docente_evaluado=docente)

        suma_est = sum([sum(extraer_valores_numericos(e.respuestas)) for e in est if isinstance(e.respuestas, dict)])
        count_est = sum([len(extraer_valores_numericos(e.respuestas)) for e in est if isinstance(e.respuestas, dict)])
        if count_est > 0:
            promedios.append(suma_est / count_est)

        for grupo in [auto, directivo]:
            for eval in grupo:
                if isinstance(eval.respuestas, dict):
                    valores = extraer_valores_numericos(eval.respuestas)
                    if valores:
                        promedios.append(sum(valores) / len(valores))

        if promedios:
            ponderados_data['labels'].append(f"{docente.primer_nombre} {docente.primer_apellido}")
            ponderados_data['data'].append(round(sum(promedios) / len(promedios), 2))

    if ponderados_data['labels']:
        sorted_data = sorted(
            zip(ponderados_data['labels'], ponderados_data['data']),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        ponderados_data['labels'], ponderados_data['data'] = zip(*sorted_data)

    contexto.update({
        'programa_seleccionado': programa,
        'evaluaciones_estudiantes': evaluaciones_estudiantes_count,
        'evaluaciones_docentes': evaluaciones_docentes_count,
        'semestres_data': json.dumps(semestres_data),
        'ponderados_data': json.dumps(ponderados_data),
    })

    return render(request, 'core/graficos_por_programa.html', contexto)
