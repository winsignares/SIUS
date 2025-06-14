# Importar Librerías
import calendar
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
import traceback
import json
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

# Importar Vistas
from .utilidades import obtener_db_info, calcular_dias_laborados_por_mes, calcular_dias_laborados_por_contrato, nombre_mes
from home.templatetags.format_extras import contabilidad_co, miles_co
from home.decorators import group_required

# Importar Módelos
from home.models import Empleado, TipoContrato, Contrato, Periodo, Dedicacion, DetalleContratro, NivelAcademicoHistorico, CargaAcademica, MateriaCompartida

# Variables globales
MESES_ORDEN = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

#
# ---------------------------- TALENTO HUMANO ---------------------------------
#

@group_required("Director Talento Humano")
def definir_contrato(request, usuario_id):
    """
    Muestra el formulario para definir el contrato de un empleado.
    """
    usuario = get_object_or_404(Empleado, id=usuario_id)

    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    periodo_actual = contexto.get("periodo_actual")

    # Obtener el listado de tipos de contratos
    tipos_contrato = TipoContrato.objects.all()

    # Obtener el contrato más reciente del usuario (si existe)
    contrato = Contrato.objects.filter(fk_usuario=usuario.id, fk_periodo=periodo_actual.id).order_by('-fecha_inicio').first()

    contexto.update({
        "usuario": usuario,
        "tipos_contrato_list": tipos_contrato,
        "contrato_usuario": contrato # Pasamos un solo contrato, no una queryset
    })

    return render(
        request,
        "partials/definir_contrato.html",
        contexto,
    )


@login_required
def actualizar_detalles_contrato_existentes(request, contrato):
    '''
        Actualizar los detalles existentes por contrato
    '''
    DetalleContratro.objects.filter(fk_contrato=contrato, vigente=True).update(vigente=False)


@login_required
def generar_detalles_contrato(request, contrato):
    """
    Genera registros de detalles del contrato con días laborados y valores a pagar por mes:
    - Primer mes: días laborados y valor proporcional
    - Meses intermedios: 30 días y valor completo del valor mensual a pagar
    - Último mes: días laborados y valor proporcional
    """

    if request:
        fecha_inicio = contrato.fecha_inicio
        fecha_fin = contrato.fecha_fin
        valor_mensual = contrato.valor_mensual_contrato

        if not fecha_inicio or not fecha_fin or valor_mensual is None:
            raise ValueError("El contrato debe tener fecha de inicio, fecha de fin y un valor mensual válido.")

        valor_mensual = Decimal(valor_mensual)

        # 🔁 Aquí llamas a tu función separada
        actualizar_detalles_contrato_existentes(request, contrato)

        dias_laborados_por_mes = calcular_dias_laborados_por_mes(fecha_inicio, fecha_fin)

        detalles = []
        for (year, month), dias_laborados in sorted(dias_laborados_por_mes.items()):
            dias_en_el_mes = calendar.monthrange(year, month)[1]
            valor_dia = valor_mensual / Decimal(dias_en_el_mes)
            valor_mes = (valor_dia * Decimal(dias_laborados)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            detalles.append(
                DetalleContratro.objects.create(
                    fk_contrato=contrato,
                    mes_a_pagar=nombre_mes(month),
                    dias_laborados=dias_laborados,
                    valor_a_pagar=valor_mes,
                    vigente=True
                )
            )

            print(f"{nombre_mes(month)} {year} - {dias_laborados} días trabajados - valor mensual: {valor_mensual}, valor día: {valor_dia}, total: {valor_mes}")



@login_required
def definir_contrato_usuario(request, usuario_id):
    """
    Muestra el formulario para definir el contrato de un empleado.
    """
    if request.method == "POST":
        usuario = get_object_or_404(Empleado, id=usuario_id)
        data = request.POST
        try:
            # Instanciar valores recibidos
            fk_usuario = Empleado.objects.get(id=usuario.id)
            if fk_periodo := data.get("fk_periodo"):
                    fk_periodo = Periodo.objects.get(id=fk_periodo)
            tipo_contrato = data.get("tipo_contrato")
            if fk_dedicacion := data.get("fk_dedicacion"):
                fk_dedicacion = Dedicacion.objects.get(id=fk_dedicacion)
            inicio_contrato = data.get("fecha_inicio_contrato")
            fin_contrato = data.get("fecha_fin_contrato")
            estado_contrato = data.get("estado_contrato")
            fk_tipo_contrato = TipoContrato.objects.get(id=tipo_contrato)
            if valor_mensual_contrato := data.get("valor_mensual_contrato"):
                valor_mensual_contrato = Decimal(valor_mensual_contrato.replace(",", ""))
            total_dias_laborados_por_contrato = calcular_dias_laborados_por_contrato(inicio_contrato, fin_contrato)

            # Convertir fechas a datetime
            fecha_inicio_contrato = datetime.strptime(inicio_contrato, "%Y-%m-%d")
            fecha_fin_contrato = datetime.strptime(fin_contrato, "%Y-%m-%d")

            # Lógica segun el tipo de contrato
            if estado_contrato == "1":
                # Agregar nuevo contrato
                contrato = Contrato.objects.create(
                    fk_periodo=fk_periodo,
                    fk_usuario=fk_usuario,
                    fecha_inicio=fecha_inicio_contrato,
                    fecha_fin=fecha_fin_contrato,
                    fk_tipo_contrato=fk_tipo_contrato,
                    fk_dedicacion=fk_dedicacion,
                    vigencia_contrato=True,
                    valor_mensual_contrato=valor_mensual_contrato,
                    total_dias_laborados=total_dias_laborados_por_contrato
                )

                if valor_mensual_contrato is not None:
                    generar_detalles_contrato(request, contrato)
            if estado_contrato == "2":
                # Editar contrato existente
                print(data)
                pass

            if estado_contrato == "3":
                # Anexar contrato
                print(data)
                pass

            return JsonResponse({
                "status": "success",
                "message": "Contrato asignado correctamente."
            })
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                "status": "error",
                "message": 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)

#
# ---------------------------- CONTRATOS DOCENTES ---------------------------------
#

@group_required("Contabilidad", "Rector", "Presidente", "Director Talento Humano")
def gestion_contratos_docentes(request):
    """
    Muestra el módulo de contratos
    """
    contexto = obtener_db_info(
        request,
        incluir_datos_adicionales=True
    )

    return render(
        request,
        'docentes.html',
        contexto
    )


@login_required
def detalles_contrato_docente(request, contrato_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            contrato = Contrato.objects.select_related("fk_usuario", "fk_dedicacion", "fk_periodo").get(id=contrato_id)
            detalles = DetalleContratro.objects.filter(fk_contrato=contrato, vigente=True)

            total_dias_laborados = sum(int(detalle.dias_laborados) for detalle in detalles if detalle.dias_laborados)
            total_asigancion_mensual = sum(int(detalle.valor_a_pagar) for detalle in detalles if detalle.valor_a_pagar)

            docente = contrato.fk_usuario

            cargas = CargaAcademica.objects.filter(
                fk_docente_asignado=docente,
                fk_periodo=contrato.fk_periodo,
            ).select_related(
                "fk_materia", "fk_programa", "fk_docente_asignado"
            ).order_by('fk_semestre__semestre')

            for carga in cargas:
                programa_madre = carga.fk_programa

                # Buscar programas compartidos por esta carga
                programas_compartidos = MateriaCompartida.objects.filter(
                    fk_carga_academica=carga
                ).select_related("fk_programa")

                # Para tabla individual: string de todos los programas asociados a esa carga
                todos_los_programas = [f"{programa_madre.nombre_corto}"] + [
                    pc.fk_programa.nombre_corto for pc in programas_compartidos if pc.fk_programa
                ]
                carga.programas_compartidos_str = " - ".join(todos_los_programas)

                # Total del valor a pagar de las cargas del docente
                total_valor_cargas = sum(int(carga.valor_a_pagar) for carga in cargas if carga.valor_a_pagar)
                total_horas_semanales = sum(int(carga.horas_semanales) for carga in cargas if carga.horas_semanales)

            html = render_to_string("partials/detalles_contrato_docentes.html", {
                "contrato": contrato,
                "detalles": detalles,
                "cargas": cargas,
                "total_valor_cargas": total_valor_cargas,
                "total_horas_semanales": total_horas_semanales,
                "total_dias_laborados": total_dias_laborados,
                "total_asigancion_mensual": total_asigancion_mensual,
            }, request=request)

            return HttpResponse(html)
        except Contrato.DoesNotExist:
            return HttpResponse("<p class='text-danger'>Contrato no encontrado.</p>")
    return HttpResponse(status=400)


@login_required
def contratos_docentes(request):
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user = request.user
        periodo_actual = contexto['periodo_actual']

        # Si no hay periodo, retornar vacío
        if not periodo_actual:
            return JsonResponse({"contratos": []})

        # Docentes con contrato vigente
        docentes = Empleado.objects.filter(fk_rol_id__in=[2, 4, 8], fk_estado_revision=1, activo=True)
        contratos = Contrato.objects.filter(fk_usuario__in=docentes, fk_periodo=periodo_actual, vigencia_contrato=True)

        # Aplicar filtro adicional por rol
        if user.groups.filter(name="Contabilidad").exists():
            contratos = contratos.filter(
                fk_usuario__in=Empleado.objects.filter(
                    cargaacademica__fk_periodo=periodo_actual,
                    cargaacademica__aprobado_vicerrectoria=True
                ).distinct()
            )
        elif user.groups.filter(name="Rector").exists():
            contratos = contratos.filter(aprobado_contabilidad=True)
        elif user.groups.filter(name="Presidente").exists():
            contratos = contratos.filter(aprobado_rectoria=True)

        contratos = contratos.select_related('fk_usuario').order_by('fk_usuario__primer_nombre', 'fk_usuario__segundo_nombre', 'fk_usuario__primer_apellido', 'fk_usuario__segundo_apellido')

        data = []
        for c in contratos:
            tarifa = None
            valor_hora = None
            if c.fk_usuario and c.fk_usuario.fk_ultimo_nivel_estudio:
                nivel = c.fk_usuario.fk_ultimo_nivel_estudio
                año = c.fk_periodo.year if hasattr(c.fk_periodo, "year") else datetime.now().year
                tarifa = NivelAcademicoHistorico.objects.filter(fk_nivel_academico=nivel, año_vigencia=año).first()
                # Solo si la dedicación es HC (id=1), se envía el valor de la hora
                if c.fk_dedicacion_id == 1 and tarifa:
                    valor_hora = contabilidad_co(tarifa.tarifa_base_por_hora)
                else:
                    valor_hora = ""

            detalle_contrato = DetalleContratro.objects.filter(fk_contrato=c, vigente=True)
            detalle_list = [
                {
                    "mes": d.mes_a_pagar,
                    "dias": d.dias_laborados,
                    "valor": contabilidad_co(d.valor_a_pagar)
                }
                for d in detalle_contrato
            ]
            # Ordenar detalle_list por el índice del mes en MESES_ORDEN
            detalle_list.sort(key=lambda x: MESES_ORDEN.index(x["mes"].split()[0]))

            data.append({
                "docente": f"{c.fk_usuario.primer_nombre} {c.fk_usuario.primer_apellido} {c.fk_usuario.segundo_apellido}" if c.fk_usuario else "",
                "documento": f"{c.fk_usuario.fk_tipo_documento.tipo_documento} - {miles_co(c.fk_usuario.numero_documento)}",
                "ultimo_nivel_estudio": c.fk_usuario.fk_ultimo_nivel_estudio.nombre,
                "tarifa_base_por_hora": valor_hora,
                "dedicacion": c.fk_dedicacion.nombre_corto if c.fk_dedicacion else "",
                "fecha_inicio": c.fecha_inicio,
                "fecha_fin": c.fecha_fin,
                "valor_mensual_contrato": contabilidad_co(c.valor_mensual_contrato) or contabilidad_co(0),
                "pago_por_mes": detalle_list,
                "aprobado_contabilidad": c.aprobado_contabilidad,
                "aprobado_rectoria": c.aprobado_rectoria,
                "aprobado_presidencia": c.aprobado_presidencia,
                "id": c.id
            })
        return JsonResponse({"contratos": data})
    return JsonResponse({"contratos": []})


#
# ---------------------------- CONTRATOS ADMINISTRATIVOS ---------------------------------
#

@group_required("Contabilidad", "Rector", "Presidente")
def gestion_contratos_administrativos(request):
    """
    Muestra el módulo de administrativos (Dpto Contablilidad)
    """
    contexto = obtener_db_info(
        request,
        incluir_datos_adicionales=True
    )

    # Filtrar usuarios con rol de administrativo
    administrativos = Empleado.objects.filter(
        fk_rol__descripcion="Administrativo"
    ).order_by(
        '-fecha_modificacion'
    )

    # Agregar los administrativos al contexto
    contexto.update({
        "administrativos": administrativos,
        "dia_actual": datetime.now().date(),
    })

    return render(
        request,
        'administrativos.html',
        contexto
    )


@login_required
def aprobar_contrato_contabilidad(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        contrato_id = data.get("contrato_id")
        aprobado = data.get("aprobado")
        try:
            contrato = Contrato.objects.get(id=contrato_id)
            contrato.aprobado_contabilidad = aprobado
            contrato.fk_aprobado_contabilidad = request.user if aprobado else None
            contrato.fecha_aprobacion_contabilidad = timezone.now() if aprobado else None
            contrato.save()
            return JsonResponse({
                "status": "success",
                "message": "Contrato aprobado." if aprobado else "Aprobación retirada."
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


@login_required
def aprobar_contratos_contabilidad(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        try:
            # Obtener el periodo actual por fechas
            hoy = timezone.now().date()
            periodo_actual = Periodo.objects.filter(fecha_apertura__lte=hoy, fecha_cierre__gte=hoy).first()
            if not periodo_actual:
                return JsonResponse({
                    "status": "error",
                    "message": "No hay un periodo activo."
                }, status=400)

            contratos = Contrato.objects.filter(
                fk_periodo=periodo_actual,
                vigencia_contrato = True
            )
            now = timezone.now()
            for contrato in contratos:
                contrato.aprobado_contabilidad = True
                contrato.fk_aprobado_contabilidad = request.user
                contrato.fecha_aprobacion_contabilidad = now
                contrato.save()
            return JsonResponse({
                "status": "success",
                "message": "Contratos aprobados correctamente."
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "status": "error",
                "message": "No se pudo aprobar todos los contratos."
            }, status=400)
    return JsonResponse({
        "status": "error",
        "message": "Petición inválida."
    }, status=400)


@login_required
def aprobar_contrato_rectoria(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        contrato_id = data.get("contrato_id")
        aprobado = data.get("aprobado")
        try:
            contrato = Contrato.objects.get(id=contrato_id)
            contrato.aprobado_rectoria = aprobado
            contrato.fk_aprobado_rectoria = request.user if aprobado else None
            contrato.fecha_aprobacion_rectoria = timezone.now() if aprobado else None
            contrato.save()
            return JsonResponse({
                "status": "success",
                "message": "Contrato aprobado." if aprobado else "Aprobación retirada."
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


@login_required
def aprobar_contratos_rectoria(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        try:
            # Obtener el periodo actual por fechas
            hoy = timezone.now().date()
            periodo_actual = Periodo.objects.filter(fecha_apertura__lte=hoy, fecha_cierre__gte=hoy).first()
            if not periodo_actual:
                return JsonResponse({
                    "status": "error",
                    "message": "No hay un periodo activo."
                }, status=400)

            contratos = Contrato.objects.filter(
                fk_periodo=periodo_actual,
                vigencia_contrato = True
            )
            now = timezone.now()
            for contrato in contratos:
                contrato.aprobado_rectoria = True
                contrato.fk_aprobado_rectoria = request.user
                contrato.fecha_aprobacion_rectoria = now
                contrato.save()
            return JsonResponse({
                "status": "success",
                "message": "Contratos aprobados correctamente."
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "status": "error",
                "message": "No se pudo aprobar todos los contratos."
            }, status=400)
    return JsonResponse({
        "status": "error",
        "message": "Petición inválida."
    }, status=400)


@login_required
def aprobar_contrato_presidencia(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        contrato_id = data.get("contrato_id")
        aprobado = data.get("aprobado")
        try:
            contrato = Contrato.objects.get(id=contrato_id)
            contrato.aprobado_presidencia = aprobado
            contrato.fk_aprobado_presidencia = request.user if aprobado else None
            contrato.fecha_aprobacion_presidencia = timezone.now() if aprobado else None
            contrato.save()
            return JsonResponse({
                "status": "success",
                "message": "Contrato aprobado." if aprobado else "Aprobación retirada."
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