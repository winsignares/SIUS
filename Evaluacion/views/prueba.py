from ..models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from home.models.carga_academica import CargaAcademica
from django.db.models import Avg
def obtener_calificaciones_estudiantes_por_docente():
    evaluaciones = EvaluacionEstudiante.objects.all()
    
    # Diccionario para almacenar suma y cantidad por docente
    docente_suma = {}
    docente_cantidad = {}
    
    for ev in evaluaciones:
        # Supongamos que la calificación total está en ev.respuestas['total'] (ajusta esto según tu JSON)
        calificacion = ev.respuestas.get('total', 0)  # Cambia 'total' por la clave real
        
        # Obtener el docente asignado a la materia (relacionado con carga académica)
        carga = CargaAcademica.objects.filter(fk_materia=ev.materia).first()
        if not carga:
            continue
        docente = carga.fk_docente_asignado
        
        if docente not in docente_suma:
            docente_suma[docente] = 0
            docente_cantidad[docente] = 0
        
        docente_suma[docente] += calificacion
        docente_cantidad[docente] += 1
    
    # Calcular promedio por docente
    promedios = []
    for docente, suma in docente_suma.items():
        promedio = suma / docente_cantidad[docente] if docente_cantidad[docente] > 0 else 0
        promedios.append({'docente': docente, 'promedio_calificacion': promedio})
    
    return promedios

def obtener_calificaciones_directivo():
    # Obtiene promedio de calificaciones de evaluaciones directivas agrupadas por docente evaluado
    return (
        EvaluacionDirectivo.objects
        .values('docente_evaluado')
        .annotate(promedio_calificacion=Avg('calificacion'))  # Requiere campo 'calificacion' en EvaluacionDirectivo
    )

def obtener_calificaciones_autoevaluacion_docente():
    # Obtiene promedio de calificaciones de autoevaluaciones agrupadas por docente
    return (
        EvaluacionDocente.objects
        .values('docente')
        .annotate(promedio_calificacion=Avg('calificacion'))  # Requiere campo 'calificacion' en EvaluacionDocente
    )

def calcular_desempeno_docentes():
    # Junta los datos de las tres evaluaciones en un solo dict
    estudiantes = list(obtener_calificaciones_estudiantes_por_docente())
    directivos = list(obtener_calificaciones_directivo())
    autoevaluacion = list(obtener_calificaciones_autoevaluacion_docente())

    return {
        "estudiantes": estudiantes,
        "directivos": directivos,
        "autoevaluacion": autoevaluacion
    }

def categorizar_desempeno(promedio):
    if promedio is None:
        return "Sin datos"
    elif promedio >= 4.5:
        return "Excelente"
    elif promedio >= 3.5:
        return "Bueno"
    elif promedio >= 2.5:
        return "Regular"
    else:
        return "Insuficiente"

def calcular_desempeno_docentes_categorizado():
    datos = calcular_desempeno_docentes()

    resultados = {
        "estudiantes": [],
        "directivos": [],
        "autoevaluacion": []
    }

    for eval_tipo in ["estudiantes", "directivos", "autoevaluacion"]:
        for item in datos[eval_tipo]:
            promedio = item.get('promedio_calificacion')
            docente_id = None

            if eval_tipo == "estudiantes":
                docente_id = item.get('materia__cargaacademica__fk_docente_asignado')
            elif eval_tipo == "directivos":
                docente_id = item.get('docente_evaluado')
            elif eval_tipo == "autoevaluacion":
                docente_id = item.get('docente')

            desempeño = categorizar_desempeno(promedio)

            resultados[eval_tipo].append({
                "docente_id": docente_id,
                "promedio": promedio,
                "desempeño": desempeño
            })

    return resultados

from Evaluacion.models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from home.models.carga_academica import CargaAcademica
from django.db.models import Avg
from Evaluacion.views.prueba import obtener_calificaciones_estudiantes_por_docente, calcular_desempeno_docentes
