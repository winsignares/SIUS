# Importar Librerías
from datetime import datetime
from decimal import Decimal
import traceback
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

# Importar Vistas
from .utilidades import obtener_db_info, calcular_dias_laborados_por_mes, calcular_dias_laborados_por_contrato

# Importar Módelos
from home.models import Empleado, Programa, TipoContrato, Contrato, Periodo, Dedicacion, DetalleContratro


#
# ---------------------------- TALENTO HUMANO ---------------------------------
#

@login_required
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
        "partials/detalle_contrato.html",
        contexto,
    )


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
        # DetalleContratro.objects.filter(fk_contrato=contrato).delete()

        # Calcular días laborados por mes
        dias_laborados_por_mes = calcular_dias_laborados_por_mes(fecha_inicio, fecha_fin)
        meses_ordenados = sorted(dias_laborados_por_mes.keys())
        valor_dia = valor_mensual / 30

        detalles = []

        for idx, mes in enumerate(meses_ordenados):
            dias = dias_laborados_por_mes[mes]
            # Primer mes
            if idx == 0:
                if dias == 30:
                    valor_mes = valor_mensual
                else:
                    valor_mes = round(dias * valor_dia, 2)
            # Último mes
            elif idx == len(meses_ordenados) - 1:
                if dias == 30:
                    valor_mes = valor_mensual
                else:
                    valor_mes = round(dias * valor_dia, 2)
            # Meses intermedios
            else:
                dias = 30
                valor_mes = valor_mensual

            detalles.append(
                DetalleContratro(
                    fk_contrato=contrato,
                    mes_a_pagar=mes,
                    dias_laborados=dias,
                    valor_a_pagar=valor_mes,
                )
            )

        DetalleContratro.objects.bulk_create(detalles)
        return detalles


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
# ---------------------------- CONTABILIDAD ---------------------------------
#

def gestion_contratos_docentes(request):
    """
    Muestra el módulo de contratos (Dpto Contablilidad)
    """
    contexto = obtener_db_info(
        request,
        incluir_datos_adicionales=True
    )

    contexto.update({
        'programa_list': Programa.objects.all(),
    })

    return render(
        request,
        'docentes.html',
        contexto
    )


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
