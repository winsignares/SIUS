# Importar Librerías
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
import traceback

# Importar Modelos
from home.models import Contrato


@login_required
def ver_contrato_docente_pdf(request, contrato_id):
    try:
        contrato = get_object_or_404(Contrato, id=contrato_id)

        # Validar si está aprobado por Presidencia
        if not contrato.aprobado_presidencia:
            return HttpResponse("Contrato no autorizado para generación de PDF", status=403)

        docente = contrato.fk_usuario

        if contrato.fk_dedicacion == 1:
            plantilla = "formatos_contrato/contrato_docentes_hc.html"
        elif contrato.fk_dedicacion != 1:
            if docente.fk_rol.id == 8:
                plantilla = "formatos_contrato/contrato_docentes_investigador.html"
            elif docente.fk_rol.id == 2:
                plantilla = "formatos_contrato/contrato_docentes_administrativo.html"
            else:
                plantilla = "formatos_contrato/contrato_docentes_tc_o_mt.html"


        # Renderizar HTML desde plantilla
        html_string = render_to_string(plantilla, {
            "contrato": contrato,
            "docente": docente,
        })

        # Generar PDF con WeasyPrint
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

        # Nombre del archivo
        nombre_archivo = slugify(f"{docente.primer_nombre}_{docente.segundo_apellido}_{docente.numero_documento}") + ".pdf"

        # Respuesta HTTP
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{nombre_archivo}"'
        return response

    except Exception as e:
        print(traceback.format_exc())
        return HttpResponse("Ha ocurrido un error al generar el PDF del contrato.", status=500)
