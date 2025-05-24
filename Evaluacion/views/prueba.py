from ..models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from django.db.models import Avg
from home.models.talento_humano.usuarios import Usuario

PONDERACIONES = {
    "estudiantes": 0.4,
    "directivos": 0.4,
    "autoevaluacion": 0.2,
}

def obtener_calificaciones_estudiantes_por_docente():
    evaluaciones = EvaluacionEstudiante.objects.select_related('materia')
    resultados = []

    for evaluacion in evaluaciones:
        respuestas = evaluacion.respuestas
        if respuestas:
            calificaciones = [int(v) for v in respuestas.values()]
            promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0
            carga_academica = evaluacion.materia.cargaacademica_set.first()

            if carga_academica:
                resultados.append({
                    # Aquí la clave es 'docente', no 'docente_id'
                    'docente': carga_academica.fk_docente_asignado.id,
                    'promedio_calificacion': promedio,
                })

    return resultados


def obtener_calificaciones_directivo():
    evaluaciones = EvaluacionDirectivo.objects.all()
    resultados = []

    for evaluacion in evaluaciones:
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


def obtener_calificaciones_autoevaluacion_docente():
    """
    Obtiene el promedio de calificaciones de autoevaluación por docente, procesando los datos en Python.
    """
    evaluaciones = EvaluacionDocente.objects.select_related('docente')

    resultados = []
    for evaluacion in evaluaciones:
        respuestas = evaluacion.respuestas  # JSON con {pregunta_id: respuesta}
        valores = [valor for valor in respuestas.values() if isinstance(valor, (int, float))]
        promedio_calificacion = sum(valores) / len(valores) if valores else None

        usuario = Usuario.objects.filter(auth_user=evaluacion.docente).first()
        resultados.append({
            'docente_id': usuario.id if usuario else None,
            'usuario_id': evaluacion.docente.id,
            'promedio_calificacion': promedio_calificacion,
        })

    return resultados


def calcular_desempeno_docentes_categorizado():
    estudiantes = obtener_calificaciones_estudiantes_por_docente()
    directivos = obtener_calificaciones_directivo()
    autoevaluacion = obtener_calificaciones_autoevaluacion_docente()

    resultados = {}

    # Ajuste aquí: clave 'docente' en estudiantes
    for item in estudiantes:
        docente_id = item['docente']  
        promedio = item['promedio_calificacion']
        if docente_id not in resultados:
            resultados[docente_id] = {'estudiantes': 0, 'directivos': 0, 'autoevaluacion': 0}
        resultados[docente_id]['estudiantes'] = promedio

    # Aquí la clave es 'docente_evaluado' en directivos
    for item in directivos:
        docente_id = item['docente_evaluado']
        promedio = item['promedio_calificacion']
        if docente_id not in resultados:
            resultados[docente_id] = {'estudiantes': 0, 'directivos': 0, 'autoevaluacion': 0}
        resultados[docente_id]['directivos'] = promedio

    # Aquí la clave es 'docente_id' en autoevaluacion
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


def categorizar_desempeno(promedio):
    if promedio >= 4.5:
        return "Excelente"
    elif promedio >= 4.0:
        return "Bueno"
    elif promedio >= 3.5:
        return "Aceptable"
    else:
        return "Bajo"


# Importaciones finales si las necesitas
from Evaluacion.models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from Evaluacion.views.prueba import calcular_desempeno_docentes_categorizado, categorizar_desempeno, obtener_calificaciones_autoevaluacion_docente