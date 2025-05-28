from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from Evaluacion.views.info_db import obtener_db_info
from home.models.carga_academica.datos_adicionales import Programa
from Evaluacion.models import EvaluacionEstudiante, EvaluacionDocente, EvaluacionDirectivo
from home.models.talento_humano.usuarios import Empleado
import openpyxl
from django.contrib.auth.decorators import login_required


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
            continue  

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
        if programa_id and evaluacion.docente_evaluado.programa_id != int(programa_id):
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
        usuario = Empleado.objects.filter(auth_user=evaluacion.docente).first()
        if programa_id and usuario and usuario.programa_id != int(programa_id):
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
            usuario = Empleado.objects.filter(id=docente_id).first()
            item['docente_nombre'] = usuario.__str__() if usuario else "Desconocido"
        else:
            item['docente_nombre'] = "Desconocido"
    return lista

@login_required
def desempeno_por_programa(request):
    programas = Programa.objects.all()
    programa_seleccionado = request.GET.get('programa', None)
    funcion = request.GET.get('funcion', None)  # Botón presionado

    estudiantes = []
    directivos = []
    autoevaluacion = []
    desempeno = []

    if programa_seleccionado:
        docentes_relacionados = Empleado.objects.filter(programa__id=programa_seleccionado)

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

    contexto = obtener_db_info(request)

    contexto.update({
        'programas': programas,
        'estudiantes': estudiantes,
        'directivos': directivos,
        'autoevaluacion': autoevaluacion,
        'desempeno': desempeno,
        'programa_seleccionado': programa_seleccionado,
    })
    return render(request, 'core/promedios_docentes.html', contexto)

def exportar_informe_excel(request):
    programa_seleccionado = request.GET.get('programa', None)
    tipo_informe = request.GET.get('tipo', None)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Informe"

    # Selección de encabezados y datos según el tipo de informe
    if tipo_informe == "general":
        encabezados = ["Docente", "Promedio", "Desempeño"]
        data = calcular_desempeno_docentes_categorizado(programa_seleccionado)
        data = agregar_nombre_docente(data, "docente_id")

    elif tipo_informe == "docente_individual":
        encabezados = ["Docente", "Asignatura", "Promedio Estudiantes", "Promedio Directivos", "Promedio Autoevaluación"]
        autoevaluacion = obtener_calificaciones_autoevaluacion_docente(programa_seleccionado)
        estudiantes = obtener_calificaciones_estudiantes_por_docente(programa_seleccionado)
        directivos = obtener_calificaciones_directivo(programa_seleccionado)
        data = merge_informe_docente(autoevaluacion, estudiantes, directivos)

    elif tipo_informe == "ranking":
        encabezados = ["Docente", "Promedio", "Desempeño"]
        data = calcular_desempeno_docentes_categorizado(programa_seleccionado)
        data = agregar_nombre_docente(data, "docente_id")
        data = sorted(data, key=lambda x: x["promedio"], reverse=True)[:10]

    elif tipo_informe == "programa_formacion":
        encabezados = ["Docente", "Promedio General", "Áreas Críticas"]
        data = generar_informe_programa_formacion(programa_seleccionado)

    else:
        # Tipo de informe no válido
        response = HttpResponse("Tipo de informe no válido", status=400)
        return response

    # Escribir encabezados en el Excel
    sheet.append(encabezados)

    # Añadir datos al archivo Excel
    for item in data:
        row = []
        for encabezado in encabezados:
            clave = encabezado.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
            if clave == "docente":  # Manejar clave especial para docente
                valor = item.get("docente_nombre", "Desconocido")
            else:
                valor = item.get(clave, "Desconocido")
            row.append(valor)
        sheet.append(row)

    # Configuración de la respuesta
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{tipo_informe}_informe.xlsx"'
    workbook.save(response)
    return response


def merge_informe_docente(autoevaluacion, estudiantes, directivos):
    docentes = {}

    for item in autoevaluacion:
        docente_id = item["docente_id"]
        docentes[docente_id] = {
            "docente": item.get("docente_nombre", "Desconocido"),
            "autoevaluacion": item.get("promedio_calificacion", "-"),
        }

    for item in estudiantes:
        docente_id = item["docente"]
        if docente_id not in docentes:
            docentes[docente_id] = {"docente": item.get("docente_nombre", "Desconocido")}
        docentes[docente_id]["estudiantes"] = item.get("promedio_calificacion", "-")

    for item in directivos:
        docente_id = item["docente_evaluado"]
        if docente_id not in docentes:
            docentes[docente_id] = {"docente": item.get("docente_nombre", "Desconocido")}
        docentes[docente_id]["directivos"] = item.get("promedio_calificacion", "-")

    # Preparar lista para exportar
    resultado = []
    for docente_id, datos in docentes.items():
        resultado.append({
            "docente": datos.get("docente", "Desconocido"),
            "asignatura": "-",  # Podrías añadir si hay datos
            "promedio_estudiantes": datos.get("estudiantes", "-"),
            "promedio_directivos": datos.get("directivos", "-"),
            "promedio_autoevaluacion": datos.get("autoevaluacion", "-"),
        })
    return resultado

def generar_informe_programa_formacion(programa_id):
    # Aquí deberías implementar el cálculo para el informe por programa de formación,
    # según tus datos específicos y necesidades.
    # Por ahora dejo un ejemplo vacío.
    return []