from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Evaluacion.views.info_db import obtener_db_info
from ..models import CategoriaDirectivo, EvaluacionDirectivo, EvaluacionDocente, EvaluacionEstudiante
from home.models.talento_humano.usuarios import Empleado, EmpleadoUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from home.models.carga_academica.datos_adicionales import Periodo, ProgramaUser, Materia
from django.utils.timezone import now
from home.models.carga_academica.carga_academica import CargaAcademica
from django.db.models import Count, Avg
from collections import defaultdict
import json

@login_required
def listado_docentes(request):
    def extraer_valores_numericos(respuestas):
        valores = []
        for v in respuestas.values():
            try:
                valores.append(float(v))
            except (ValueError, TypeError):
                continue
        return valores

    usuario_actual = ProgramaUser.objects.filter(fk_user=request.user).select_related('fk_programa').first()
    contexto = obtener_db_info(request)

    if not usuario_actual:
        mensaje_error = "No se encontró información asociada a tu cuenta. Contacta al administrador."
        return render(request, 'core/listado_docentes.html', {'mensaje_error': mensaje_error})

    if not usuario_actual.fk_programa:
        mensaje_error = "No tienes un programa asignado. Por favor, contacta a la administración."
        return render(request, 'core/listado_docentes.html', {'mensaje_error': mensaje_error})

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).order_by('-fecha_apertura').first()

    if not periodo_activo:
        mensaje_error = "No hay un periodo activo configurado. Contacta al administrador."
        contexto.update({'mensaje_error': mensaje_error})
        return render(request, 'core/listado_docentes.html', contexto)

    cargas = CargaAcademica.objects.filter(
        fk_programa=usuario_actual.fk_programa
    ).select_related('fk_docente_asignado')

    docentes_programa = {carga.fk_docente_asignado for carga in cargas if carga.fk_docente_asignado}

    if not docentes_programa:
        mensaje_advertencia = "No hay docentes disponibles con carga académica en tu programa."
        contexto.update({'mensaje_advertencia': mensaje_advertencia})
        return render(request, 'core/listado_docentes.html', contexto)

    evaluaciones_estudiantes_count = EvaluacionEstudiante.objects.filter(
        periodo=periodo_activo,
        materia__fk_programa=usuario_actual.fk_programa
    ).values('estudiante').distinct().count()

    evaluaciones_docentes_count = EvaluacionDocente.objects.filter(
        periodo=periodo_activo,
        docente__in=docentes_programa
    ).count()

    evaluaciones_por_semestre = EvaluacionEstudiante.objects.filter(
        periodo=periodo_activo,
        materia__fk_programa=usuario_actual.fk_programa
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

    ponderados_data = {'labels': [], 'data': []}

    for docente in docentes_programa:
        eval_estudiantes = EvaluacionEstudiante.objects.filter(
            periodo=periodo_activo,
            docente_evaluado=docente,
            materia__fk_programa=usuario_actual.fk_programa
        )

        eval_autoevaluaciones = EvaluacionDocente.objects.filter(
            periodo=periodo_activo,
            docente=docente
        )

        eval_director = EvaluacionDirectivo.objects.filter(
            periodo=periodo_activo,
            docente_evaluado=docente
        )

        promedios = []

        suma_estudiantes = 0
        count_estudiantes = 0
        for eval_est in eval_estudiantes:
            if isinstance(eval_est.respuestas, dict):
                valores = extraer_valores_numericos(eval_est.respuestas)
                if valores:
                    suma_estudiantes += sum(valores)
                    count_estudiantes += len(valores)
        if count_estudiantes > 0:
            promedios.append(suma_estudiantes / count_estudiantes)

        for eval_auto in eval_autoevaluaciones:
            if isinstance(eval_auto.respuestas, dict):
                valores = extraer_valores_numericos(eval_auto.respuestas)
                if valores:
                    promedios.append(sum(valores) / len(valores))

        for eval_dir in eval_director:
            if isinstance(eval_dir.respuestas, dict):
                valores = extraer_valores_numericos(eval_dir.respuestas)
                if valores:
                    promedios.append(sum(valores) / len(valores))

        if promedios:
            ponderado_final = sum(promedios) / len(promedios)
            ponderados_data['labels'].append(f"{docente.primer_nombre} {docente.primer_apellido}")
            ponderados_data['data'].append(round(ponderado_final, 2))

    if ponderados_data['labels']:
        sorted_data = sorted(
            zip(ponderados_data['labels'], ponderados_data['data']),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        ponderados_data['labels'] = [x[0] for x in sorted_data]
        ponderados_data['data'] = [x[1] for x in sorted_data]

    docentes_evaluados_ids = set(EvaluacionDirectivo.objects.filter(
        periodo=periodo_activo,
        docente_evaluado__in=docentes_programa
    ).values_list('docente_evaluado_id', flat=True))

    docentes_unicos = list(docentes_programa)
    paginator = Paginator(docentes_unicos, 8)
    page = request.GET.get('page')

    try:
        docentes_paginados = paginator.page(page)
    except PageNotAnInteger:
        docentes_paginados = paginator.page(1)
    except EmptyPage:
        docentes_paginados = paginator.page(paginator.num_pages)

    contexto.update({
        'docentes': docentes_paginados,
        'docentes_evaluados_ids': docentes_evaluados_ids,
        'periodo': periodo_activo,
        'evaluaciones_estudiantes': evaluaciones_estudiantes_count,
        'evaluaciones_docentes': evaluaciones_docentes_count,
        'semestres_data': json.dumps(semestres_data),
        'ponderados_data': json.dumps(ponderados_data)
    })

    return render(request, 'core/listado_docentes.html', contexto)


@login_required
def evaluar_docente(request, docente_id):
   
    docente_evaluado = get_object_or_404(Empleado, id=docente_id)
    evaluador = request.user

    
    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    if not periodo_activo:
        messages.error(request, "No hay un periodo activo configurado. Contacta al administrador.")
        return redirect('evaluacion:listado_docentes')

    
    categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    
    evaluacion_existente = EvaluacionDirectivo.objects.filter(
        evaluador=evaluador,
        docente_evaluado=docente_evaluado,
        periodo=periodo_activo
    ).first()

    if request.method == 'POST':
        if evaluacion_existente:
            messages.warning(request, "Ya realizaste esta evaluación para el periodo activo.")
            return redirect('evaluacion:listado_docentes')

        # Procesar las respuestas enviadas en el formulario
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
            periodo=periodo_activo,
            respuestas=respuestas
        )

        messages.success(request, f"Evaluación registrada correctamente para el docente {docente_evaluado.primer_apellido}.")
        return redirect('evaluacion:listado_docentes')

    
    context = {
        'docente': docente_evaluado,
        'preguntas_por_categoria': preguntas_por_categoria,
        'evaluacion_existente': evaluacion_existente,
        'periodo': periodo_activo
    }
    return render(request, 'core/evaluar_docente.html', context)
