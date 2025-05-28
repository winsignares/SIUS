# Importar Librerías
import traceback
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# Importar Módelos
from home.models import Empleado, DetalleAcademico, DetalleExperienciaLaboral


@login_required
def agregar_detalle_academico(request):
    if request.method == "POST":
        print(request.POST)
        usuario_id = request.POST.get("usuario_id")
        institucion = request.POST.get("institucion")
        institucion_extranjera = request.POST.get("institucion_extranjera")
        codigo_convalidacion = request.POST.get("codigo_convalidacion")
        titulo_obtenido = request.POST.get("titulo_obtenido")
        nivel_academico_id = request.POST.get("nivel_academico")
        metodologia_programa = request.POST.get("metodologia_programa")
        ies_codigo = request.POST.get("ies_codigo")
        codigo_pais = request.POST.get("codigo_pais")
        fecha_graduacion = request.POST.get("fecha_graduacion")

        try:
            # Validar que el usuario existe
            usuario = get_object_or_404(Empleado, id=usuario_id)

            # Validar campos numéricos
            if ies_codigo and not ies_codigo.isdigit():
                return JsonResponse({
                    "status": "error",
                    "message": "El código IES debe ser numérico."
                }, status=400)

            if codigo_pais and not codigo_pais.isdigit():
                return JsonResponse({
                    "status": "error",
                    "message": "El código del país debe ser numérico."
                }, status=400)

            # Crear el detalle académico
            detalle = DetalleAcademico.objects.create(
                usuario=usuario,
                institucion=institucion,
                institucion_extranjera=institucion_extranjera,
                codigo_convalidacion=codigo_convalidacion,
                titulo_obtenido=titulo_obtenido,
                nivel_academico_id=nivel_academico_id,
                metodologia_programa=metodologia_programa,
                ies_codigo=ies_codigo if ies_codigo else None,
                codigo_pais=codigo_pais if codigo_pais else None,
                fecha_graduacion=fecha_graduacion
            )

            contexto = {
                "detalle": {
                    "institucion": detalle.institucion,
                    "titulo_obtenido": detalle.titulo_obtenido,
                    "institucion_extranjera": detalle.institucion_extranjera,
                    "codigo_convalidacion": detalle.codigo_convalidacion,
                    "nivel_academico": detalle.nivel_academico.nombre,
                    "metodologia_programa": detalle.metodologia_programa,
                    "ies_codigo": detalle.ies_codigo,
                    "codigo_pais": detalle.codigo_pais,
                    "fecha_graduacion": detalle.fecha_graduacion,
                }
            }

            return JsonResponse({
                "status": "success",
                "message": "Detalle académico agregado exitosamente.",
                "detalle": contexto["detalle"]
            })

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                "status": "error",
                "message": 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)


@login_required
def agregar_exp_laboral(request):
    if request.method == "POST":
        print(request.POST)
        usuario_id = request.POST.get("usuario_id")
        empresa = request.POST.get("empresa")
        cargo = request.POST.get("cargo")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        laborando_actualmente = request.POST.get("laborando_actualmente") == "on"

        try:
            # Validar que el usuario existe
            usuario = get_object_or_404(Empleado, id=usuario_id)

            # Si está laborando actualmente, establecer fecha_fin como None
            if laborando_actualmente or fecha_fin == "":
                fecha_fin = None

            # Crear el detalle de experiencia laboral
            detalle = DetalleExperienciaLaboral.objects.create(
                usuario=usuario,
                empresa=empresa,
                cargo=cargo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                trabajando_actualmente=laborando_actualmente
            )

            contexto = {
                "detalle": {
                    "empresa": detalle.empresa,
                    "cargo": detalle.cargo,
                    "fecha_inicio": detalle.fecha_inicio,
                    "fecha_fin": detalle.fecha_fin if detalle.fecha_fin else "Actualmente"
                }
            }

            return JsonResponse({
                "status": "success",
                "message": "Experiencia laboral agregada exitosamente.",
                "detalle": contexto["detalle"]
            })

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                "status": "error",
                "message": 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)