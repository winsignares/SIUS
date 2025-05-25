# Importar Librerías
import traceback
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, models
from django.shortcuts import render
from django.http import JsonResponse


# Importar Vistas
from .utilidades import obtener_db_info

# Importar Módelos
from home.models import Empleado, NivelAcademico, Departamento, Sede, EstadoRevision, AFP, CajaCompensacion, ARL

@login_required
def gestion_empleados(request):
    '''
        Función que maneja la vista de Empleados
    '''
    # Obtener contexto con datos adicionales
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    # Capturar parámetros de búsqueda
    # Término de búsqueda para aspirantes en estado 'Pendiente'
    empleado_activo = request.GET.get('empleado_activo', '').strip()
    empleados_activos = Empleado.objects.filter(activo=True, fk_estado_revision=1).order_by('-fecha_modificacion')
    # Término de búsqueda para aspirantes en estado 'Rechazado'
    empleado_inactivo = request.GET.get('empleado_inactivo', '').strip()
    empleados_inactivos = Empleado.objects.filter(activo=False, fk_estado_revision=1).order_by('-fecha_modificacion')

    # Filtrar datos si hay una búsqueda
    if empleado_activo:
        empleados_activos = empleados_activos.filter(
            models.Q(primer_nombre__icontains=empleado_activo) |
            models.Q(segundo_nombre__icontains=empleado_activo) |
            models.Q(primer_apellido__icontains=empleado_activo) |
            models.Q(segundo_apellido__icontains=empleado_activo) |
            models.Q(numero_documento__icontains=empleado_activo) |
            models.Q(fk_rol__descripcion__icontains=empleado_activo)
        )
    elif empleado_inactivo:
        empleados_inactivos = empleados_inactivos.filter(
            models.Q(primer_nombre__icontains=empleado_inactivo) |
            models.Q(segundo_nombre__icontains=empleado_inactivo) |
            models.Q(primer_apellido__icontains=empleado_inactivo) |
            models.Q(segundo_apellido__icontains=empleado_inactivo) |
            models.Q(numero_documento__icontains=empleado_inactivo) |
            models.Q(fk_rol__descripcion__icontains=empleado_inactivo)
        )

    numero_registros = 10
    # Paginación para la tabla de aspirantes en estado 'Activos'
    paginator_activos = Paginator(empleados_activos, numero_registros)  # 5 registros por página
    page_number_activos = request.GET.get('page_activos')
    page_obj_activos = paginator_activos.get_page(page_number_activos)

    # Paginación para la tabla de aspirantes en estado 'Inactivos'
    paginator_inactivos = Paginator(empleados_inactivos, numero_registros)  # 8 registros por página
    page_number_inactivos = request.GET.get('page_inactivos')
    page_obj_inactivos = paginator_inactivos.get_page(page_number_inactivos)

    # Actualizar el contexto
    contexto.update({
        'page_obj_activos': page_obj_activos,
        'page_obj_inactivos': page_obj_inactivos,
        'empleado_activo': empleado_activo,
        'empleado_inactivo': empleado_inactivo,
    })

    return render(request, 'empleados.html', contexto)



@login_required
def agregar_empleado(request):
    print(request.POST)
    if request.method == 'POST':
        data = request.POST
        try:
            # Verificar si ya existe un usuario con el número de documento ingresado
            if Empleado.objects.filter(numero_documento=data.get('numero_documento')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un empleado con el número de documento ingresado.'
                }, status=400)

            # Verificar si ya existe un usuario con el correo
            if Empleado.objects.filter(correo_personal=data.get('correo_personal')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un empleado con el correo personal ingresado.'
                }, status=400)

            # Instanciar ForeignKeys
            fk_ultimo_nivel_estudio_ins = NivelAcademico.objects.get(id=data.get('fk_ultimo_nivel_estudio_emp'))
            fk_afp_ins = AFP.objects.get(id=data.get('fk_afp_emp'))
            fk_arl_ins = ARL.objects.get(id=data.get('fk_arl_emp'))
            fk_caja_compensacion_ins = CajaCompensacion.objects.get(id=data.get('fk_caja_compensacion_emp'))
            fk_departamento_residencia_ins = Departamento.objects.get(id=data.get('fk_departamento_residencia_emp'))
            fk_sede_donde_labora_ins = Sede.objects.get(id=data.get('fk_sede_donde_labora_emp'))
            fk_estado_revision_ins = EstadoRevision.objects.get(id=data.get('fk_estado_revision_emp'))

            nuevo_usuario = Empleado.objects.create(
                # Campos obligatorios
                fk_rol_id= data.get('fk_rol_emp'),
                fk_tipo_documento_id=data.get('fk_tipo_documento_emp'),
                cargo=data.get('cargo_emp'),
                primer_nombre=data.get('primer_nombre_emp'),
                primer_apellido=data.get('primer_apellido_emp'),
                numero_documento=data.get('numero_documento_emp'),
                correo_personal=data.get('correo_personal_emp'),
                fk_estado_revision=fk_estado_revision_ins,
                # Campos opcionales
                segundo_nombre=data.get('segundo_nombre_emp'),
                segundo_apellido=data.get('segundo_apellido_emp'),
                fecha_nacimiento=data.get('fecha_nacimiento_emp'),
                lugar_nacimiento=data.get('lugar_nacimiento_emp'),
                fecha_expedicion_documento=data.get('fecha_expedicion_documento_emp'),
                lugar_expedicion_documento=data.get('lugar_expedicion_documento_emp'),
                sexo=data.get('sexo_emp'),
                telefono_fijo=data.get('telefono_fijo_emp'),
                celular=data.get('celular_emp'),
                estado_civil=data.get('estado_civil_emp'),
                fk_ultimo_nivel_estudio=fk_ultimo_nivel_estudio_ins,
                fk_eps_id=data.get('fk_eps_emp'),
                fk_arl=fk_arl_ins,
                fk_afp=fk_afp_ins,
                fk_caja_compensacion=fk_caja_compensacion_ins,
                direccion_residencia=data.get('direccion_residencia_emp'),
                fk_departamento_residencia=fk_departamento_residencia_ins,
                ciudad_residencia=data.get('ciudad_residencia_emp'),
                barrio_residencia=data.get('barrio_residencia_emp'),
                fk_sede_donde_labora=fk_sede_donde_labora_ins,
                url_hoja_de_vida=data.get('url_hoja_de_vida_emp'),
                fk_creado_por=request.user,
                activo=True
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Empleado agregado correctamente.',
                'usuario_id': nuevo_usuario.id
            })

        except IntegrityError as e:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado. Por favor, intente nuevamente.'
            }, status=400)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)
