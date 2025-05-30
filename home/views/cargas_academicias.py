# Importar Librerías
from collections import defaultdict
from itertools import chain
from datetime import datetime
import traceback
import json
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Sum, Value, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


# Importar Vistas
from .utilidades import obtener_db_info, calcular_valor_a_pagar
from home.templatetags.format_extras import contabilidad_co, miles_co


# Importar Módelos
from home.models import Empleado, CargaAcademica, MateriaCompartida, Contrato, Periodo, Programa, Semestre, Materia


#
# ---------------------------- FUNCIONES SUSTANTIVAS ---------------------------------
#


@login_required
def gestion_func_sustantivas(request):
    """
    Muestra la gestión de funciones sustantivas
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    dia_actual = datetime.now().date()

    contexto.update({
            "dia_actual": dia_actual,
        })

    return render(request, 'func_sustantivas.html', contexto)


#
# ---------------------------- CARGA ACADEMICA ---------------------------------
#


@login_required
def gestion_carga_academica(request):
    """
    Muestra la gestión de carga académica, filtrando los semestres según el programa del usuario.
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    programa_usuario = contexto["programa_usuario"]
    periodo_actual = contexto["periodo_actual"]

    # Cargas propias (programa madre)
    cargas_propias = CargaAcademica.objects.filter(
        fk_periodo=periodo_actual,
        fk_programa=programa_usuario
    )

    # Cargas compartidas (donde el usuario es "invitado")
    cargas_compartidas_ids = MateriaCompartida.objects.filter(
        fk_programa=programa_usuario,
        fk_periodo=periodo_actual
    ).values_list('fk_carga_academica_id', flat=True)

    cargas_compartidas = CargaAcademica.objects.filter(id__in=cargas_compartidas_ids)

    # Unir ambos querysets y eliminar duplicados
    cargas_academicas = list({c.id: c for c in chain(cargas_propias, cargas_compartidas)}.values())

    # Diccionario de programas compartidos para cada carga
    materias_compartidas_dict = {}
    for carga in cargas_academicas:
        # Programas con los que se comparte (no incluye el programa madre)
        programas = MateriaCompartida.objects.filter(fk_carga_academica=carga).values_list('fk_programa__programa', flat=True)
        materias_compartidas_dict[carga.id] = list(programas)

    # Agrupar cargas académicas por semestre
    cargas_dict = defaultdict(list)
    for carga in cargas_academicas:
        cargas_dict[carga.fk_semestre.semestre].append(carga)

    # Calcular total valor_a_pagar por semestre usando ORM para eficiencia
    ids_cargas = [c.id for c in cargas_academicas]
    totales_qs = CargaAcademica.objects.filter(id__in=ids_cargas).values('fk_semestre__semestre').annotate(total_valor=Sum(Coalesce('valor_a_pagar', Value(0))))

    # Convertir queryset a dict para acceso fácil en template
    totales_por_semestre = {
        item['fk_semestre__semestre']: item['total_valor'] or 0 for item in totales_qs
    }

    # Convertir a diccionario normal para el template
    contexto["cargas_dict"] = dict(cargas_dict)
    contexto["totales_por_semestre"] = totales_por_semestre
    contexto["materias_compartidas_dict"] = materias_compartidas_dict
    contexto["cargas_academicas"] = cargas_academicas

    return render(request, 'carga_academica.html', contexto)


#
# ---------------------------- MATRIZ DE CARGA ACADEMICA ---------------------------------
#


@login_required
def gestion_matriz(request):
    """
    Muestra la gestión
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    dia_actual = datetime.now().date()

    contexto.update({
            "dia_actual": dia_actual,
        })

    return render(request, 'matriz.html', contexto)


@login_required
def guardar_matriz(request):
    """
    Guarda la carga académica del usuario.
    """
    if request.method == "POST":
        # Obtener datos del formulario
        data = json.loads(request.body)

        try:
            for carga in data["cargas"]:
                print(carga)
                # Instanciar los datos enviados desde el front
                fk_periodo_inst = Periodo.objects.get(id=carga["fk_periodo"])
                fk_programa_inst = Programa.objects.get(id=carga["fk_programa"])
                fk_semestre_inst = Semestre.objects.get(id=carga["fk_semestre"])
                fk_materia_inst = Materia.objects.get(id=carga["fk_materia"])
                fk_docente_asignado_inst = Empleado.objects.get(id=carga["fk_docente_asignado"])

                # Validar que la carga académica no exista ya
                if CargaAcademica.objects.filter(
                    fk_periodo=fk_periodo_inst,
                    fk_programa=fk_programa_inst,
                    fk_semestre=fk_semestre_inst,
                    fk_materia=fk_materia_inst,
                    fk_docente_asignado=fk_docente_asignado_inst
                ).exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': 'La carga académica ya existe para este docente y materia.'
                    }, status=400)

                # Valor a pagar si la dedicación es "Hora Cátedra - HC"
                contrato = Contrato.objects.filter(fk_usuario=fk_docente_asignado_inst.id, vigencia_contrato=True).first()
                if contrato and contrato.fk_dedicacion and contrato.fk_dedicacion.id == 1:
                    valor_a_pagar = calcular_valor_a_pagar(carga["total_horas"], fk_docente_asignado_inst.id)
                else:
                    valor_a_pagar = None

                # Guardar los datos en la DB
                carga_academica = CargaAcademica.objects.create(
                    fk_periodo = fk_periodo_inst,
                    fk_programa = fk_programa_inst,
                    fk_semestre = fk_semestre_inst,
                    fk_materia = fk_materia_inst,
                    fk_docente_asignado = fk_docente_asignado_inst,
                    horas_semanales = carga["horas_semanales"],
                    total_horas = carga["total_horas"],
                    materia_compartida = carga["materia_compartida"],
                    fk_creado_por = request.user,
                    valor_a_pagar = valor_a_pagar,
                    aprobado_vicerrectoria = False,
                    aprobado_contabilidad = False,
                    aprobado_rectoria = False
                )

                # Almacenar Materias Compartidas:
                if carga.get("materia_compartida") and carga.get("programas_seleccionados_id"):
                    for programa_id in carga["programas_seleccionados_id"]:
                        MateriaCompartida.objects.create(
                            fk_carga_academica=carga_academica,
                            fk_programa_id=programa_id,
                            fk_periodo=fk_periodo_inst
                        )

            return JsonResponse({
                'status': 'success',
                'message': 'Carga académica agregada correctamente.'})
        except IntegrityError:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': 'Error al agregar la carga académica. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': "Error inesperado. Por favor, intente nuevamente."
            }, status=500)


#
# ---------------------------- APROBACIÓN DE CARGA ACADEMICA ---------------------------------
#


@login_required
def gestion_cargas_aprobaciones(request):
    """
    Muestra la gestión
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    dia_actual = datetime.now().date()

    contexto.update({
            "dia_actual": dia_actual,
        })

    return render(request, 'carga_aprobaciones.html', contexto)


@login_required
def filtrar_cargas_academicas(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        programa_id = request.GET.get("programa")
        semestre_id = request.GET.get("semestre")
        cargas = CargaAcademica.objects.all()
        if programa_id:
            cargas = cargas.filter(
                Q(fk_programa_id=programa_id) |
                Q(materiacompartida__fk_programa_id=programa_id)
            ).distinct()
        if semestre_id:
            cargas = cargas.filter(fk_semestre_id=semestre_id)

        # Prepara el diccionario de materias compartidas
        materias_compartidas_dict = {}
        for carga in cargas:
            programas = MateriaCompartida.objects.filter(
                fk_carga_academica=carga
            ).values_list('fk_programa__programa', flat=True)
            materias_compartidas_dict[carga.id] = list(programas)

        data = []
        for carga in cargas:
            # Programas compartidos (nombres)
            programas = materias_compartidas_dict.get(carga.id, [])
            # Programa madre
            programa_madre = carga.fk_programa.programa
            # Docente
            docente = f"{carga.fk_docente_asignado.primer_nombre} {carga.fk_docente_asignado.primer_apellido}"
            if carga.fk_docente_asignado.segundo_apellido:
                docente += f" {carga.fk_docente_asignado.segundo_apellido}"
            # Documento
            documento = f"{carga.fk_docente_asignado.fk_tipo_documento.tipo_documento} - {miles_co(carga.fk_docente_asignado.numero_documento)}"
            # Dedicación
            contrato = Contrato.objects.filter(fk_usuario=carga.fk_docente_asignado, vigencia_contrato=True).first()
            dedicacion = contrato.fk_dedicacion.nombre_corto if contrato and contrato.fk_dedicacion else "Sin dedicación"
            # Valor a pagar
            valor_a_pagar = contabilidad_co(carga.valor_a_pagar) if carga.valor_a_pagar else "No aplica"

            data.append({
                "materia": carga.fk_materia.materia,
                "compartida_con": [programa_madre] + [p for p in programas if p != programa_madre],
                "programa_madre": programa_madre,
                "docente": docente,
                "documento": documento,
                "dedicacion": dedicacion,
                "creditos": carga.fk_materia.creditos,
                "horas_totales": carga.total_horas,
                "valor_a_pagar": valor_a_pagar,
                "id": carga.id,
                "aprobada": carga.aprobado_vicerrectoria,
            })
        return JsonResponse({"cargas": data})
    return JsonResponse({"cargas": []})

@login_required
def aprobar_carga_academica(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        carga_id = data.get("carga_id")
        aprobada = data.get("aprobada")
        try:
            carga = CargaAcademica.objects.get(id=carga_id)
            carga.aprobado_vicerrectoria = aprobada
            carga.fk_aprobado_vicerrectoria = request.user if aprobada else None
            carga.fecha_aprobacion_vicerrectoria = timezone.now() if aprobada else None
            carga.save()
            return JsonResponse({
                "status": "success",
                "message": "Carga académica aprobada correctamente." if aprobada else "Aprobación retirada correctamente."
            }, status=200)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                "status": "error",
                "message": "No se pudo actualizar la aprobación."
            }, status=400)
    return JsonResponse({
        "status": "error",
        "message": "Petición inválida."
    }, status=400)