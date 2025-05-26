from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from home.models.carga_academica.datos_adicionales import Programa
from Evaluacion.models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from home.models.talento_humano.usuarios import Usuario

PONDERACIONES = {
    "estudiantes": 0.4,
    "directivos": 0.4,
    "autoevaluacion": 0.2,
}

def obtener_calificaciones_estudiantes_por_docente(programa_id=None):
    evaluaciones = EvaluacionEstudiante.objects.select_related('materia')
    resultados = []

    for evaluacion in evaluaciones:
        if programa_id and evaluacion.materia.fk_programa_id != int(programa_id):
            continue  # filtro por programa

        respuestas = evaluacion.respuestas
        if respuestas:
            calificaciones = [int(v) for v in respuestas.values()]
            promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0
            carga_academica = evaluacion.materia.cargaacademica_set.first()

            if carga_academica:
                resultados.append({
                    'docente': carga_academica.fk_docente_asignado.id,
                    'promedio_calificacion': promedio,
                })

    return resultados


def obtener_calificaciones_directivo(programa_id=None):
    evaluaciones = EvaluacionDirectivo.objects.all()
    resultados = []

    for evaluacion in evaluaciones:
        if programa_id and evaluacion.docente_evaluado.fk_programa_id != int(programa_id):
            continue  # filtro por programa

        respuestas = evaluacion.respuestas
        calificaciones = [int(valor) for valor in respuestas.values()]
        promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0

        docente_evaluado_id = evaluacion.docente_evaluado.id
        existente = next((item for item in resultados if item['docente_evaluado'] == docente_evaluado_id), None)

        if existente:
            existente['promedio_calificacion'].append(promedio)
        else:
            resultados.append({
                'docente_evaluado': docente_evaluado_id,
                'promedio_calificacion': [promedio],
            })

    for resultado in resultados:
        resultado['promedio_calificacion'] = sum(resultado['promedio_calificacion']) / len(resultado['promedio_calificacion'])

    return resultados


def obtener_calificaciones_autoevaluacion_docente(programa_id=None):
    evaluaciones = EvaluacionDocente.objects.select_related('docente')

    resultados = []
    for evaluacion in evaluaciones:
        usuario = Usuario.objects.filter(auth_user=evaluacion.docente).first()
        if programa_id and usuario and usuario.fk_programa_id != int(programa_id):
            continue  # filtro por programa

        respuestas = evaluacion.respuestas
        valores = [valor for valor in respuestas.values() if isinstance(valor, (int, float))]
        promedio_calificacion = sum(valores) / len(valores) if valores else None

        resultados.append({
            'docente_id': usuario.id if usuario else None,
            'usuario_id': evaluacion.docente.id,
            'promedio_calificacion': promedio_calificacion,
        })

    return resultados


def categorizar_desempeno(promedio):
    if promedio >= 4.5:
        return "Excelente"
    elif promedio >= 4.0:
        return "Bueno"
    elif promedio >= 3.5:
        return "Aceptable"
    else:
        return "Bajo"


def calcular_desempeno_docentes_categorizado(programa_id=None):
    estudiantes = obtener_calificaciones_estudiantes_por_docente(programa_id)
    directivos = obtener_calificaciones_directivo(programa_id)
    autoevaluacion = obtener_calificaciones_autoevaluacion_docente(programa_id)

    resultados = {}

    for item in estudiantes:
        docente_id = item['docente']  
        promedio = item['promedio_calificacion']
        if docente_id not in resultados:
            resultados[docente_id] = {'estudiantes': 0, 'directivos': 0, 'autoevaluacion': 0}
        resultados[docente_id]['estudiantes'] = promedio

    for item in directivos:
        docente_id = item['docente_evaluado']
        promedio = item['promedio_calificacion']
        if docente_id not in resultados:
            resultados[docente_id] = {'estudiantes': 0, 'directivos': 0, 'autoevaluacion': 0}
        resultados[docente_id]['directivos'] = promedio

    for item in autoevaluacion:
        docente_id = item['docente_id']
        promedio = item['promedio_calificacion']
        if docente_id not in resultados:
            resultados[docente_id] = {'estudiantes': 0, 'directivos': 0, 'autoevaluacion': 0}
        resultados[docente_id]['autoevaluacion'] = promedio

    desempeno = []
    for docente_id, promedios in resultados.items():
        promedio_ponderado = (
            promedios['estudiantes'] * PONDERACIONES['estudiantes'] +
            promedios['directivos'] * PONDERACIONES['directivos'] +
            promedios['autoevaluacion'] * PONDERACIONES['autoevaluacion']
        )
        desempeno.append({
            'docente_id': docente_id,
            'promedio': promedio_ponderado,
            'desempeño': categorizar_desempeno(promedio_ponderado),
        })

    return desempeno


def agregar_nombre_docente(lista, key_id):
    for item in lista:
        docente_id = item.get(key_id)
        if docente_id:
            usuario = Usuario.objects.filter(id=docente_id).first()
            item['docente_nombre'] = usuario.__str__() if usuario else "Desconocido"
        else:
            item['docente_nombre'] = "Desconocido"
    return lista


def desempeno_por_programa(request):
    programas = Programa.objects.all()
    programa_seleccionado = request.GET.get('programa', None)
    funcion = request.GET.get('funcion', None)  # Botón presionado

    estudiantes = []
    directivos = []
    autoevaluacion = []
    desempeno = []

    if programa_seleccionado:
        docentes_relacionados = Usuario.objects.filter(programa__id=programa_seleccionado)

        if funcion == 'estudiantes':
            estudiantes = obtener_calificaciones_estudiantes_por_docente()
            estudiantes = [
                item for item in estudiantes if item['docente'] in docentes_relacionados.values_list('id', flat=True)
            ]
            estudiantes = agregar_nombre_docente(estudiantes, 'docente')

        elif funcion == 'directivos':
            directivos = obtener_calificaciones_directivo()
            directivos = [
                item for item in directivos if item['docente_evaluado'] in docentes_relacionados.values_list('id', flat=True)
            ]
            directivos = agregar_nombre_docente(directivos, 'docente_evaluado')

        elif funcion == 'autoevaluacion':
            autoevaluacion = obtener_calificaciones_autoevaluacion_docente()
            autoevaluacion = [
                item for item in autoevaluacion if item['docente_id'] in docentes_relacionados.values_list('id', flat=True)
            ]
            autoevaluacion = agregar_nombre_docente(autoevaluacion, 'docente_id')

        elif funcion == 'desempeno':
            desempeno = calcular_desempeno_docentes_categorizado()
            desempeno = [
                item for item in desempeno if item['docente_id'] in docentes_relacionados.values_list('id', flat=True)
            ]
            desempeno = agregar_nombre_docente(desempeno, 'docente_id')

    context = {
        'programas': programas,
        'estudiantes': estudiantes,
        'directivos': directivos,
        'autoevaluacion': autoevaluacion,
        'desempeno': desempeno,
        'programa_seleccionado': programa_seleccionado,
    }
    return render(request, 'core/promedios_docentes.html', context)