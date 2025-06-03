from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO
from collections import defaultdict
from Evaluacion.views.info_db import obtener_db_info

from ..models import CategoriaDocente, CategoriaEstudiante, EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo, CategoriaDirectivo
from home.models.carga_academica import CargaAcademica
from home.models.talento_humano import Empleado
from home.models.carga_academica.datos_adicionales import Periodo, Programa, Materia

@login_required
def reporte_selector(request):
    docentes = Empleado.objects.filter(fk_rol__rol='D')
        
    docentes_carga = docentes.filter(cargaacademica__isnull=False).distinct()
    programas = Programa.objects.all()
    periodos = Periodo.objects.all()

    contexto = obtener_db_info(request)
    contexto.update( {
        'docentes': docentes_carga,
        'programas': programas,
        'periodos': periodos,
    })
    return render(request, 'reportes/reportes.html', contexto)

def render_pdf(template_src, context_dict):
    html_string = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error al generar el PDF', status=500)

@login_required
def reporte_estudiantes_docente(request):
    docente_id = request.GET.get('docente_id')
    periodo_id = request.GET.get('periodo_id')

    docente = get_object_or_404(Empleado, id=docente_id)
    periodo = get_object_or_404(Periodo, id=periodo_id)

    cargas = CargaAcademica.objects.filter(fk_docente_asignado=docente, fk_periodo=periodo)
    materias = [c.fk_materia for c in cargas]

    evaluaciones = EvaluacionEstudiante.objects.filter(
        materia__in=materias,
        periodo=periodo,
        docente_evaluado=docente
    )

    # Crear estructura: promedios_por_materia[materia_id][pregunta_id] = [respuestas]
    respuestas_agrupadas = defaultdict(lambda: defaultdict(list))

    for evaluacion in evaluaciones:
        materia_id = evaluacion.materia.id
        for pregunta_id_str, valor in evaluacion.respuestas.items():
            try:
                pregunta_id = int(pregunta_id_str)
                respuestas_agrupadas[materia_id][pregunta_id].append(int(valor))
            except (ValueError, TypeError):
                continue

    # Calcular promedios
    promedios_preguntas_por_materia = defaultdict(dict)

    for materia_id, preguntas_dict in respuestas_agrupadas.items():
        for pregunta_id, respuestas in preguntas_dict.items():
            if respuestas:
                promedio = round(sum(respuestas) / len(respuestas), 2)
                promedios_preguntas_por_materia[materia_id][pregunta_id] = promedio

    categorias = CategoriaEstudiante.objects.prefetch_related('preguntas').all()
    
    # Calcular promedio por categoría (por materia)
    promedios_categoria_por_materia = defaultdict(dict)

    for carga in cargas:
        materia_id = carga.fk_materia.id
        for categoria in categorias:
            promedios_categoria = []
            for pregunta in categoria.preguntas.all():                
                promedio = promedios_preguntas_por_materia.get(carga.fk_materia.id, {}).get(pregunta.id)
                if promedio is not None:
                    promedios_categoria.append(promedio)
            if promedios_categoria:
                promedio_categoria = round(sum(promedios_categoria) / len(promedios_categoria), 2)
                promedios_categoria_por_materia[materia_id][categoria.id] = promedio_categoria


    

    # 4. (Opcional) Promedio general por materia
    materia_promedios = {}
    for carga in cargas:
        respuestas = evaluaciones.filter(materia=carga.fk_materia).values_list('respuestas', flat=True)
        
        lista = []
        for r in respuestas:
            lista.extend([int(v) for v in r.values()])
        if lista:
            materia_promedios[carga.fk_materia.materia] = round(sum(lista) / len(lista), 2)

    # Creamos un diccionario anidado: 
    # frecuencias_relativas[materia_id][pregunta_id] = {1: freq_1, 2: freq_2, ..., 5: freq_5}
    frecuencias_relativas = defaultdict(lambda: defaultdict(dict))

    # Recorremos las respuestas agrupadas por materia y pregunta
    for materia_id, preguntas_dict in respuestas_agrupadas.items():
        for pregunta_id, respuestas in preguntas_dict.items():

            # Total de respuestas válidas para esa pregunta en esa materia
            total = len(respuestas)

            # Inicializamos un contador para cada valor posible (1 a 5) de la escala
            conteos = {valor: 0 for valor in range(1, 6)}

            # Contamos cuántas veces aparece cada valor en las respuestas
            for r in respuestas:
                if r in conteos:
                    conteos[r] += 1

            # Calculamos la frecuencia relativa: frecuencia = conteo / total * valor de la respuesta
            # Solo si hay al menos una respuesta (evitamos división por cero)
            frecuencias = {
                valor: round(conteos[valor] / total * valor, 2)
                for valor in conteos
                if total > 0
            }

            # Guardamos las frecuencias en el diccionario final
            frecuencias_relativas[materia_id][pregunta_id] = frecuencias

    return render_pdf('reportes/base_reportes.html', {
        'docente': docente,
        'periodo': periodo,
        'cargas': cargas,
        'evaluaciones': evaluaciones,
        'materia_promedios': materia_promedios,
        'categorias_estudiante': categorias,
        'promedios_preguntas_por_materia': promedios_preguntas_por_materia,
        'promedios_categoria_por_materia': promedios_categoria_por_materia,
        'tipo_evaluacion': 'EVALUACIÓN ESTUDIANTES',
        'frecuencias_relativas': frecuencias_relativas,
        'valores_escala': [1, 2, 3, 4, 5],
    })

@login_required
def reporte_directivo_programa(request):
    programa_id = request.GET.get('programa_id')
    periodo_id = request.GET.get('periodo_id')
    programa = get_object_or_404(Programa, id=programa_id)
    periodo = get_object_or_404(Periodo, id=periodo_id)

    docentes = Empleado.objects.filter(
        id__in=CargaAcademica.objects.filter(
            fk_programa=programa, 
            fk_periodo=periodo
        ).values_list('fk_docente_asignado', flat=True).distinct()
    )
    evaluaciones = EvaluacionDirectivo.objects.filter(docente_evaluado__in=docentes, periodo=periodo)

    respuestas_agrupadas = defaultdict(lambda: defaultdict(list))

    for evaluacion in evaluaciones:
        docente_id = evaluacion.docente_evaluado
        for pregunta_id_str, valor in evaluacion.respuestas.items():
            try:
                pregunta_id = int(pregunta_id_str)
                respuestas_agrupadas[docente_id][pregunta_id].append(int(valor))
            except (ValueError, TypeError):
                continue

    # Calcular promedios
    promedios_preguntas_por_docente = defaultdict(dict)

    for docente_id, preguntas_dict in respuestas_agrupadas.items():
        for pregunta_id, respuestas in preguntas_dict.items():
            if respuestas:
                promedio = round(sum(respuestas) / len(respuestas), 2)
                promedios_preguntas_por_docente[docente_id][pregunta_id] = promedio

    categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()
    
    # Calcular promedio por categoría (por docente)
    promedios_categoria_por_docente = defaultdict(dict)

    for docente in docentes:
        docente_id = docente.id
        for categoria in categorias:
            promedios_categoria = []
            for pregunta in categoria.preguntas.all():                
                promedio = promedios_preguntas_por_docente.get(docente, {}).get(pregunta.id)
                if promedio is not None:
                    promedios_categoria.append(promedio)
            if promedios_categoria:
                promedio_categoria = round(sum(promedios_categoria) / len(promedios_categoria), 2)
                promedios_categoria_por_docente[docente_id][categoria.id] = promedio_categoria

    # 4. (Opcional) Promedio general por docente
    docente_promedios = {}
    for docente in docentes:
        respuestas = evaluaciones.filter(docente_evaluado=docente).values_list('respuestas', flat=True)
        
        lista = []
        for r in respuestas:
            lista.extend([int(v) for v in r.values()])
        if lista:
            docente_promedios[docente.numero_documento] = round(sum(lista) / len(lista), 2)

    frecuencias_relativas = defaultdict(lambda: defaultdict(dict))
    for docente_id, preguntas_dict in respuestas_agrupadas.items():
        for pregunta_id, respuestas in preguntas_dict.items():

            total = len(respuestas)

            # Inicializamos un contador para cada valor posible (1 a 5) de la escala
            conteos = {valor: 0 for valor in range(1, 6)}

            # Contamos cuántas veces aparece cada valor en las respuestas
            for r in respuestas:
                if r in conteos:
                    conteos[r] += 1

            # Calculamos la frecuencia relativa: frecuencia = conteo / total * valor de la respuesta
            # Solo si hay al menos una respuesta (evitamos división por cero)
            frecuencias = {
                valor: round(conteos[valor] / total * valor, 2)
                for valor in conteos
                if total > 0
            }

            # Guardamos las frecuencias en el diccionario final
            frecuencias_relativas[docente_id][pregunta_id] = frecuencias
        

    return render_pdf('reportes/base_reportes.html', {
        'docentes': docentes,
        'periodo': periodo,
        'programa': programa,
        'evaluaciones': evaluaciones,
        'docentes_promedios': docente_promedios,
        'categorias_directivo': categorias,
        'promedios_preguntas_por_docente': promedios_preguntas_por_docente,
        'promedios_categoria_por_docente': promedios_categoria_por_docente,
        'tipo_evaluacion': 'EVALUACIÓN DIRECTIVO',
        'frecuencias_relativas': frecuencias_relativas,
        'valores_escala': [1, 2, 3, 4, 5],
    })


@login_required
def reporte_autoevaluaciones(request):
    periodo_id = request.GET.get('periodo_id')
    periodo = get_object_or_404(Periodo, id=periodo_id)

    docentes = Empleado.objects.filter(
        id__in=CargaAcademica.objects.filter(
            fk_periodo=periodo
        ).values_list('fk_docente_asignado', flat=True).distinct()
    )
    evaluaciones = EvaluacionDocente.objects.filter(docente__in=docentes, periodo=periodo)

    respuestas_agrupadas = defaultdict(lambda: defaultdict(list))

    for evaluacion in evaluaciones:
        docente_id = evaluacion.docente
        for pregunta_id_str, valor in evaluacion.respuestas.items():
            try:
                pregunta_id = int(pregunta_id_str)
                respuestas_agrupadas[docente_id][pregunta_id].append(int(valor))
            except (ValueError, TypeError):
                continue

    # Calcular promedios
    promedios_preguntas_por_docente = defaultdict(dict)

    for docente_id, preguntas_dict in respuestas_agrupadas.items():
        for pregunta_id, respuestas in preguntas_dict.items():
            if respuestas:
                promedio = round(sum(respuestas) / len(respuestas), 2)
                promedios_preguntas_por_docente[docente_id][pregunta_id] = promedio

    categorias = CategoriaDocente.objects.prefetch_related('preguntas').all()
    
    # Calcular promedio por categoría (por docente)
    promedios_categoria_por_docente = defaultdict(dict)

    for docente in docentes:
        docente_id = docente.id
        for categoria in categorias:
            promedios_categoria = []
            for pregunta in categoria.preguntas.all():                
                promedio = promedios_preguntas_por_docente.get(docente, {}).get(pregunta.id)
                if promedio is not None:
                    promedios_categoria.append(promedio)
            if promedios_categoria:
                promedio_categoria = round(sum(promedios_categoria) / len(promedios_categoria), 2)
                promedios_categoria_por_docente[docente_id][categoria.id] = promedio_categoria

    # 4. (Opcional) Promedio general por docente
    docente_promedios = {}
    for docente in docentes:
        respuestas = evaluaciones.filter(docente=docente).values_list('respuestas', flat=True)
        
        lista = []
        for r in respuestas:
            lista.extend([int(v) for v in r.values()])
        if lista:
            docente_promedios[docente.numero_documento] = round(sum(lista) / len(lista), 2)

    frecuencias_relativas = defaultdict(lambda: defaultdict(dict))
    for docente_id, preguntas_dict in respuestas_agrupadas.items():
        for pregunta_id, respuestas in preguntas_dict.items():

            total = len(respuestas)

            # Inicializamos un contador para cada valor posible (1 a 5) de la escala
            conteos = {valor: 0 for valor in range(1, 6)}

            # Contamos cuántas veces aparece cada valor en las respuestas
            for r in respuestas:
                if r in conteos:
                    conteos[r] += 1

            # Calculamos la frecuencia relativa: frecuencia = conteo / total * valor de la respuesta
            # Solo si hay al menos una respuesta (evitamos división por cero)
            frecuencias = {
                valor: round(conteos[valor] / total * valor, 2)
                for valor in conteos
                if total > 0
            }

            # Guardamos las frecuencias en el diccionario final
            frecuencias_relativas[docente_id][pregunta_id] = frecuencias
        

    return render_pdf('reportes/base_reportes.html', {
        'docentes': docentes,
        'periodo': periodo,
        'evaluaciones': evaluaciones,
        'docentes_promedios': docente_promedios,
        'categorias_directivo': categorias,
        'promedios_preguntas_por_docente': promedios_preguntas_por_docente,
        'promedios_categoria_por_docente': promedios_categoria_por_docente,
        'tipo_evaluacion': 'AUTOEVALUACIÓN DOCENTE',
        'frecuencias_relativas': frecuencias_relativas,
        'valores_escala': [1, 2, 3, 4, 5],
    })
