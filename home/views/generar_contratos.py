# Importar Librerías
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
import traceback

# Importar Modelos
from home.models import Contrato, CargaAcademica, EmpleadoUser, MateriaCompartida


@login_required
def ver_contrato_docente_pdf(request, contrato_id):
    try:
        contrato = get_object_or_404(Contrato, id=contrato_id)

        if not contrato.aprobado_presidencia:
            return HttpResponse("Contrato no autorizado para generación de PDF", status=403)

        docente = contrato.fk_usuario

        cargas = CargaAcademica.objects.filter(
            fk_docente_asignado=docente,
            fk_periodo=contrato.fk_periodo,
        ).select_related(
            "fk_materia", "fk_programa", "fk_docente_asignado"
        ).order_by('fk_semestre__semestre')

        # Set para evitar duplicados
        programas_vinculados = set()

        for carga in cargas:
            programa_madre = carga.fk_programa
            if programa_madre:
                programas_vinculados.add(f"{programa_madre.programa} - {programa_madre.sede or 'Sin Sede'}")

            # Buscar programas compartidos por esta carga
            programas_compartidos = MateriaCompartida.objects.filter(
                fk_carga_academica=carga
            ).select_related("fk_programa")

            for pc in programas_compartidos:
                if pc.fk_programa:
                    programas_vinculados.add(f"{pc.fk_programa.programa} - {pc.fk_programa.sede or 'Sin Sede'}")

            # Para tabla individual: string de todos los programas asociados a esa carga
            todos_los_programas = [f"{programa_madre.nombre_corto}"] + [
                pc.fk_programa.nombre_corto for pc in programas_compartidos if pc.fk_programa
            ]
            carga.programas_compartidos_str = " - ".join(todos_los_programas)


        # Calcular totales
        total_horas_semanales = sum(int(carga.horas_semanales) for carga in cargas if carga.horas_semanales)
        total_horas_totales = sum(int(carga.total_horas) for carga in cargas if carga.total_horas)
        total_valor_cargas = sum(int(carga.valor_a_pagar) for carga in cargas if carga.valor_a_pagar)


        # Seleccionar plantilla según dedicación y rol
        if contrato.fk_dedicacion_id == 1:  # HC
            plantilla = "formatos_contrato/contrato_docentes_hc.html"
        elif docente.fk_rol_id == 8:
            plantilla = "formatos_contrato/contrato_docentes_investigador.html"
        elif docente.fk_rol_id == 2:
            plantilla = "formatos_contrato/contrato_docentes_administrativo.html"
        else:
            plantilla = "formatos_contrato/contrato_docentes_tc_o_mt.html"

        fecha_actual = timezone.now().date()

        # Valor total mensual + auxilio (si aplica)
        total_a_pagar = (contrato.valor_mensual_contrato or 0) + (contrato.fk_periodo.auxilio_transporte or 0)

        # Obtener el usuario que aprobó el contrato (Presidente)
        usuario_presidente = contrato.fk_aprobado_presidencia  # Es un User

        # Buscar el Empleado asociado al usuario que aprobó
        presidente_empleado = EmpleadoUser.objects.filter(fk_user=usuario_presidente).select_related("fk_empleado").first()

        # Validar que exista el vínculo
        if not presidente_empleado:
            return HttpResponse("No se encontró el representante legal vinculado al usuario.", status=404)

        # Extraer el empleado
        presidente = presidente_empleado.fk_empleado

        html_string = render_to_string(plantilla, {
            "contrato": contrato,
            "docente": docente,
            "fecha_actual": fecha_actual,
            "total_a_pagar": total_a_pagar if docente.fk_rol_id == 2 else contrato.valor_mensual_contrato,
            "total_horas_semanales": total_horas_semanales,
            "total_horas_totales": total_horas_totales,
            "total_valor_cargas": total_valor_cargas,
            "cargas": cargas,
            "presidente": presidente,
            "programas_dictados": sorted(programas_vinculados),
        })

        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

        nombre_archivo = slugify(f"{docente.primer_nombre}_{docente.segundo_nombre}_{docente.primer_apellido}_{docente.segundo_apellido}".lower()) + ".pdf"

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{nombre_archivo}"'
        return response

    except Exception as e:
        print(traceback.format_exc())
        return HttpResponse("Ha ocurrido un error al generar el PDF del contrato.", status=500)

