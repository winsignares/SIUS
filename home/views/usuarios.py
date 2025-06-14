# Importar Librerías
import traceback
from django.db import IntegrityError, models
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render

# Importar Vistas
from .utilidades import obtener_db_info
from home.decorators import group_required

# Importar Módelos
from home.models import Empleado, Rol, TipoDocumento, DetalleAcademico, DetalleExperienciaLaboral, NivelAcademico, Departamento, Sede, EstadoRevision, AFP, ARL, EPS, CajaCompensacion, Contrato, Pais


#
# ---------------------------- ASPIRANTES ---------------------------------
#


# Revisado ✅
@group_required('Secretaria Talento Humano', 'Director Talento Humano')
def gestion_aspirantes(request):
    '''
        Función que maneja la vista de Aspirantes.
    '''
    # Obtener contexto con datos adicionales
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    # Capturar parámetros de búsqueda
    # Término de búsqueda para aspirantes en estado 'Pendiente'
    aspirante_pendiente = request.GET.get('aspirante_pendiente', '').strip()
    usuarios_aspirantes = Empleado.objects.filter(
        fk_estado_revision=2).order_by('-fecha_modificacion')
    # Término de búsqueda para aspirantes en estado 'Rechazado'
    aspirante_rechazado = request.GET.get('aspirante_rechazado', '').strip()
    usuarios_rechazados = Empleado.objects.filter(
        fk_estado_revision=3).order_by('-fecha_modificacion')

    # Filtrar datos si hay una búsqueda
    if aspirante_pendiente:
        usuarios_aspirantes = usuarios_aspirantes.filter(
            models.Q(primer_nombre__icontains=aspirante_pendiente) |
            models.Q(segundo_nombre__icontains=aspirante_pendiente) |
            models.Q(primer_apellido__icontains=aspirante_pendiente) |
            models.Q(segundo_apellido__icontains=aspirante_pendiente) |
            models.Q(numero_documento__icontains=aspirante_pendiente) |
            models.Q(fk_rol__descripcion__icontains=aspirante_pendiente)
        )
    elif aspirante_rechazado:
        usuarios_rechazados = usuarios_rechazados.filter(
            models.Q(primer_nombre__icontains=aspirante_rechazado) |
            models.Q(segundo_nombre__icontains=aspirante_rechazado) |
            models.Q(primer_apellido__icontains=aspirante_rechazado) |
            models.Q(segundo_apellido__icontains=aspirante_rechazado) |
            models.Q(numero_documento__icontains=aspirante_rechazado) |
            models.Q(fk_rol__descripcion__icontains=aspirante_rechazado)
        )

    numero_registros = 10
    # Paginación para la tabla de aspirantes en estado 'Pendiente'
    paginator_pendientes = Paginator(usuarios_aspirantes, numero_registros)  # 5 registros por página
    page_number_pendientes = request.GET.get('page_pendientes')
    page_obj_pendientes = paginator_pendientes.get_page(page_number_pendientes)

    # Paginación para la tabla de aspirantes en estado 'Pendiente'
    paginator_rechazados = Paginator(usuarios_rechazados, numero_registros)  # 8 registros por página
    page_number_rechazados = request.GET.get('page_rechazados')
    page_obj_rechazados = paginator_rechazados.get_page(page_number_rechazados)

    # Actualizar el contexto
    contexto.update({
        'page_obj_pendientes': page_obj_pendientes,
        'page_obj_rechazados': page_obj_rechazados,
        'aspirante_pendiente': aspirante_pendiente,
        'aspirante_rechazado': aspirante_rechazado,
    })

    return render(request, 'aspirantes.html', contexto)


# Revisado ✅
@login_required
def agregar_aspirante(request):
    print(request.POST)
    if request.method == 'POST':
        data = request.POST
        try:
            if Empleado.objects.filter(numero_documento=data.get('numero_documento')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un aspirante con el número de documento ingresado.'
                }, status=400)

            if Empleado.objects.filter(correo_personal=data.get('correo_personal')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un aspirante con el correo personal ingresado.'
                }, status=400)

            # Instanciar ForeignKeys
            fk_ultimo_nivel_estudio_ins = NivelAcademico.objects.get(id=data.get('fk_ultimo_nivel_estudio'))
            fk_afp_ins = AFP.objects.get(id=data.get('fk_afp'))
            fk_departamento_residencia_ins = Departamento.objects.get(id=data.get('fk_departamento_residencia'))
            fk_sede_donde_labora_ins = Sede.objects.get(id=data.get('fk_sede_donde_labora'))
            fk_estado_revision_ins = EstadoRevision.objects.get(id=data.get('fk_estado_revision'))
            fk_pais_ins = Pais.objects.get(id=data.get('fk_pais'))

            nuevo_usuario = Empleado.objects.create(
                # Campos obligatorios
                fk_rol_id= data.get('fk_rol'),
                fk_tipo_documento_id=data.get('fk_tipo_documento'),
                cargo=data.get('cargo'),
                primer_nombre=data.get('primer_nombre'),
                primer_apellido=data.get('primer_apellido'),
                numero_documento=data.get('numero_documento'),
                correo_personal=data.get('correo_personal'),
                fk_estado_revision=fk_estado_revision_ins,
                # Campos opcionales
                segundo_nombre=data.get('segundo_nombre'),
                segundo_apellido=data.get('segundo_apellido'),
                fecha_nacimiento=data.get('fecha_nacimiento'),
                fk_pais_nacimiento=fk_pais_ins,
                lugar_nacimiento=data.get('lugar_nacimiento'),
                fecha_expedicion_documento=data.get('fecha_expedicion_documento'),
                lugar_expedicion_documento=data.get('lugar_expedicion_documento'),
                sexo=data.get('sexo'),
                telefono_fijo=data.get('telefono_fijo'),
                celular=data.get('celular'),
                estado_civil=data.get('estado_civil'),
                fk_ultimo_nivel_estudio=fk_ultimo_nivel_estudio_ins,
                fk_eps_id=data.get('fk_eps'),
                fk_afp=fk_afp_ins,
                direccion_residencia=data.get('direccion_residencia'),
                fk_departamento_residencia=fk_departamento_residencia_ins,
                ciudad_residencia=data.get('ciudad_residencia'),
                barrio_residencia=data.get('barrio_residencia'),
                fk_sede_donde_labora=fk_sede_donde_labora_ins,
                url_hoja_de_vida=data.get('url_hoja_de_vida'),
                fk_creado_por=request.user,
                activo=False
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Aspirante agregado correctamente.',
                'usuario_id': nuevo_usuario.id
            })

        except IntegrityError:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad al agregar el aspirante. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)


#
# ---------------------------- EMPLEADOS ---------------------------------
#


# Revisado ✅
@group_required('Secretaria Talento Humano', 'Director Talento Humano')
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


# Revisado ✅
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
            fk_pais_ins = Pais.objects.get(id=data.get('fk_pais_emo'))

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
                fk_pais_nacimiento=fk_pais_ins,
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


#
# ---------------------------- MANEJO DE USUARIOS AGREGADOS ---------------------------------
#


# Revisado ✅
@group_required('Secretaria Talento Humano', 'Director Talento Humano')
def detalle_usuario(request, usuario_id):
    """
    Muestra los detalles de un aspirante o empleado
    """
    usuario = get_object_or_404(Empleado, id=usuario_id)
    if usuario:
        template = "partials/detalle_usuario.html"
        detalles_academicos = DetalleAcademico.objects.filter(usuario=usuario)
        detalles_laborales = DetalleExperienciaLaboral.objects.filter(usuario=usuario)
        contrato_usuario = Contrato.objects.filter(fk_usuario=usuario, vigencia_contrato=True)
    else:
        return HttpResponseNotFound("No se puede mostrar la información solicitada.")

    return render(
        request,
        template,
        {
            "usuario": usuario,
            "detalles_academicos": detalles_academicos,
            "detalles_laborales": detalles_laborales,
            'contrato_usuario': contrato_usuario
        }
    )


# Revisado ✅
@group_required('Secretaria Talento Humano', 'Director Talento Humano')
def editar_usuario(request, tipo, usuario_id):
    '''
        Función para mostrar el formulario de edición de información de empleados.
    '''
    usuario = get_object_or_404(Empleado, id=usuario_id)

    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    contexto.update({
        "usuario": usuario,
        "tipo": tipo # Pasamos un solo contrato, no una queryset
    })

    return render(
        request,
        "partials/editar_usuario_form.html",
        contexto,
    )


@login_required
def actualizar_usuario(request, usuario_id):
    print(request.POST)
    usuario = get_object_or_404(Empleado, id=usuario_id)
    if request.method == "POST":
        # Extraer todos los datos del formulario
        data = request.POST
        try:
            # Verificar si ya existe otro usuario con el mismo número de documento
            if Empleado.objects.filter(numero_documento=data.get('numero_documento')).exclude(id=usuario_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe otro usuario con el número de documento ingresado.'
                }, status=400)

            # Verificar si ya existe otro usuario con el mismo correo personal
            if Empleado.objects.filter(correo_personal=data.get('correo_personal')).exclude(id=usuario_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe otro usuario con el correo personal ingresado.'
                }, status=400)

            # Actualización de campos obligatorios
            if rol_id := request.POST.get("fk_rol"):
                usuario.fk_rol = Rol.objects.get(id=rol_id)
            if tipo_documento_id := request.POST.get("fk_tipo_documento"):
                usuario.fk_tipo_documento = TipoDocumento.objects.get(id=tipo_documento_id)
            usuario.cargo = request.POST.get("cargo", usuario.cargo)
            usuario.primer_nombre = request.POST.get("primer_nombre", usuario.primer_nombre)
            usuario.primer_apellido = request.POST.get("primer_apellido", usuario.primer_apellido)
            usuario.numero_documento = request.POST.get("numero_documento", usuario.numero_documento)
            usuario.correo_personal = request.POST.get("correo_personal", usuario.correo_personal)
            if fk_estado_revision := request.POST.get('fk_estado_revision'):
                usuario.fk_estado_revision = EstadoRevision.objects.get(id=fk_estado_revision)

            # Campos opcionales
            usuario.segundo_nombre = request.POST.get("segundo_nombre", usuario.segundo_nombre)
            usuario.segundo_apellido = request.POST.get("segundo_apellido", usuario.segundo_apellido)
            usuario.fecha_nacimiento = request.POST.get("fecha_nacimiento", usuario.fecha_nacimiento)
            usuario.lugar_nacimiento = request.POST.get("lugar_nacimiento", usuario.lugar_nacimiento)
            if pais_id := request.POST.get("fk_pais"):
                usuario.fk_pais_nacimiento = Pais.objects.get(id=pais_id)
            usuario.fecha_expedicion_documento = request.POST.get("fecha_expedicion_documento", usuario.fecha_expedicion_documento)
            usuario.lugar_expedicion_documento = request.POST.get("lugar_expedicion_documento", usuario.lugar_expedicion_documento)
            usuario.sexo = request.POST.get("sexo", usuario.sexo)
            usuario.telefono_fijo = request.POST.get("telefono_fijo", usuario.telefono_fijo)
            usuario.celular = request.POST.get("celular", usuario.celular)
            usuario.estado_civil = request.POST.get("estado_civil", usuario.estado_civil)
            if ultimo_nivel_estudio_id := request.POST.get("fk_ultimo_nivel_estudio"):
                usuario.fk_ultimo_nivel_estudio = NivelAcademico.objects.get(id=ultimo_nivel_estudio_id)
            if eps_id := request.POST.get("fk_eps"):
                usuario.fk_eps = EPS.objects.get(id=eps_id)
            if arl_id := request.POST.get("fk_arl"):
                usuario.fk_arl = ARL.objects.get(id=arl_id)
            if afp_id := request.POST.get("fk_afp"):
                usuario.fk_afp = AFP.objects.get(id=afp_id)
            if caja_compensacion_id := request.POST.get("fk_caja_compensacion"):
                usuario.fk_caja_compensacion = CajaCompensacion.objects.get(id=caja_compensacion_id)
            usuario.direccion_residencia = request.POST.get("direccion_residencia", usuario.direccion_residencia)
            if departamento_residencia_id := request.POST.get("fk_departamento_residencia"):
                usuario.fk_departamento_residencia = Departamento.objects.get(id=departamento_residencia_id)
            usuario.ciudad_residencia = request.POST.get("ciudad_residencia", usuario.ciudad_residencia)
            usuario.barrio_residencia = request.POST.get("barrio_residencia", usuario.barrio_residencia)
            if sede_donde_labora_id := request.POST.get("fk_sede_donde_labora"):
                usuario.fk_sede_donde_labora = Sede.objects.get(id=sede_donde_labora_id)
            usuario.url_hoja_de_vida = request.POST.get("url_hoja_de_vida", usuario.url_hoja_de_vida)

            # Cambiar el estado de activo según el estado de revisión
            if usuario.fk_estado_revision.id == 1:
                usuario.activo = True
            else:
                usuario.activo = False

            # Actualizar el usuario modificado por
            usuario.fk_modificado_por = request.user

            usuario.save()

            return JsonResponse({
                "status": "success",
                "message": "Usuario actualizado correctamente."
            })
        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad al agregar el usuario. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)
