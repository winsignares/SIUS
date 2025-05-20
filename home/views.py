# Importar Librerias
from collections import defaultdict
import json
import traceback
from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.db import models, IntegrityError
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.core.paginator import Paginator
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import openpyxl
from io import BytesIO
import pytz

# Importar Modelos
from .models.talento_humano.usuarios import Empleado
from .models.talento_humano.detalles_academicos import DetalleAcademico
from .models.talento_humano.detalles_exp_laboral import DetalleExperienciaLaboral
from .models.talento_humano.tipo_documentos import TipoDocumento
from .models.talento_humano.niveles_academicos import NivelAcademico
from .models.talento_humano.datos_adicionales import EPS, AFP, ARL, Departamento, CajaCompensacion, Institucion, Sede
from .models.talento_humano.roles import Rol
from .models.talento_humano.contrato import TipoContrato, Contrato, DetalleContratro
from .models.carga_academica import CargaAcademica, Materia, Periodo, Programa, Semestre


#
# ---------------------------- FUNCIONES EXTRAS ---------------------------------
#


def error_404_view(request, exception):
    """
    Vista para manejar errores 404.
    """

    return render(request, '404.html', status=404)


def obtener_db_info(request, incluir_datos_adicionales=False):
    """
        Función auxiliar para obtener información especifica del usuario autenticado.
        Además, se incluye el envío de datos de la base de dato si alguna otra función lo requiere.
    """
    usuario_autenticado = request.user
    grupos_usuario = usuario_autenticado.groups.values_list('name', flat=True)

    try:
        usuario_log = Empleado.objects.get(auth_user=usuario_autenticado)
        usuario_log.primer_nombre = usuario_log.primer_nombre.capitalize()
        usuario_log.primer_apellido = usuario_log.primer_apellido.capitalize()
        usuario_log.cargo = usuario_log.cargo.upper()
    except Empleado.DoesNotExist:
        usuario_log = None

    # Obtener el programa del usuario logueado
    programa_usuario = Programa.objects.filter(auth_user=usuario_autenticado.id).first()

    # Obtener el número de semestres del programa
    num_semestres = int(programa_usuario.numero_semestres) if programa_usuario else 0

    # Filtrar los semestres hasta el número del programa
    semestres_list = Semestre.objects.filter(id__lte=num_semestres).order_by("id")

    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    programas = Programa.objects.all().values(
        'id',
        'codigo_snies',
        'programa',
        'nivel_formacion',
        'sede',
        'numero_semestres'
    )

    # Todas las materias
    materias_list_all = Materia.objects.all().values(
        'id',
        'materia',
        'codigo',
        'fk_semestre_id',
        'fk_programa_id'
    )

    # Se filtran las materias por el programa del usuario logueado
    materias_queryset = Materia.objects.select_related('fk_semestre').filter(
        fk_programa=programa_usuario).values(
            'id',
            'materia',
            'codigo',
            'horas',
            'fk_semestre_id'
        )

    # Contexto inicial
    contexto = {
        'usuario_log': usuario_log,
        'user_groups': grupos_usuario,
        'programa_usuario': programa_usuario
    }

    # Incluir datos adicionales si es necesario para otras funciones
    if incluir_datos_adicionales:
        contexto.update({
            'tipos_documento_list': TipoDocumento.objects.all(),
            'departamentos_list': Departamento.objects.all(),
            'eps_list': EPS.objects.all().order_by('id'),
            'arl_list': ARL.objects.all(),
            'cajas_compensacion_list': CajaCompensacion.objects.all(),
            'afp_list': AFP.objects.all(),
            'niveles_academicos_list': NivelAcademico.objects.all(),
            'roles_list': Rol.objects.all(),
            'instituciones_list': Institucion.objects.all().order_by('codigo'),
            'sedes_list': Sede.objects.all(),
            'semestres_list': semestres_list,
            'programas_list': list(programas),
            'materias_list_all': list(materias_list_all),
            'materias_list': list(materias_queryset),
            'periodos_list': Periodo.objects.all(),
            'docentes_list': Empleado.objects.filter(fk_rol_id=4, estado_revision='Contratado', activo=True),
            'cargas_academicas': CargaAcademica.objects.all().order_by('id'),
            'periodo_actual': Periodo.objects.filter(fecha_apertura__lte=fecha_actual, fecha_cierre__gte=fecha_actual).first()
        })

    return contexto


#
# ---------------------------- INICIO DE SESIÓN ---------------------------------
#


def iniciar_sesion_form(request):
    '''
        Función para mostrar el formulario de inicio de sesión.
    '''

    return render(request, 'login.html')


def signin(request):
    '''
        Función para manejar los datos enviados en el formulario de inicio de sesión.
    '''
    if request.method == 'GET':
        return redirect('iniciar_sesion_form')
    elif request.method == 'POST':

        postEmail = request.POST.get('email')
        postPsw = request.POST.get('password')

        # Verificar si el usuario existe en la base de datos
        try:
            user = User.objects.get(username=postEmail)
        except User.DoesNotExist:
            messages.error(
                request, "El usuario ingresado no tiene una cuenta asociada.")
            return redirect('iniciar_sesion_form')

        user = authenticate(
            request,
            username=postEmail,
            password=postPsw
        )

        if user is None:
            messages.error(
                request, "La contraseña ingresada es incorrecta.")
            return render(request, 'login.html', {'email': postEmail})

        login(request, user)

        return redirect('dashboard')


#
# ---------------------------- REESTABLECER CONTRASEÑA ---------------------------------
#


def restablecer_contraseña_form(request):
    '''
        Función para mostrar el formulario de restablecer contraseña.
    '''

    return render(request, 'restablecer_contraseña.html')


def actualizar_contraseña(request):
    '''
        Función para manejar los datos enviados en el formulario de restablcer contraseña.
    '''
    if request.method == 'GET':
        return redirect('iniciar_sesion_form')
    elif request.method == 'POST':

        reset_email = request.POST.get('resetEmail')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')

        # Verificar si el correo ingresado existe
        try:
            user = User.objects.get(username=reset_email)
        except User.DoesNotExist:
            messages.error(
                request, "El usuario ingresado no tiene una cuenta asociada.")
            return redirect('restablecer_contraseña_form')

        # Validar si las contraseñas coinciden
        if new_password != confirm_password:
            messages.error(
                request, "Las contraseñas no coinciden. Inténtalo nuevamente.")
            return render(request, 'restablecer_contraseña.html', {'reset_email': reset_email})

        # Actualizar la contraseña
        user.set_password(new_password)
        user.save()

        # Enviar mensaje de éxito
        messages.success(
            request, "Contraseña actualizada exitosamente.")

        return render(request, 'login.html', {'email': reset_email})


#
# ---------------------------- VISTA INICIO ---------------------------------
#


@login_required
def dashboard(request):
    '''
        Función para mostrar el dashboard cuando un usuario inicia sesión.
    '''
    contexto = obtener_db_info(request)

    return render(request, 'dashboard.html', contexto)


@login_required
def cerrar_sesion(request):
    '''
        Función para redireccionar al formulario de inicio de sesión cuando se cierra sesión manualmente.
    '''
    logout(request)

    return redirect('iniciar_sesion_form')


#
# ---------------------------- VISTA ASPIRANTES ---------------------------------
#


@login_required
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
        estado_revision='Pendiente').order_by('-fecha_modificacion')
    # Término de búsqueda para aspirantes en estado 'Rechazado'
    aspirante_rechazado = request.GET.get('aspirante_rechazado', '').strip()
    usuarios_rechazados = Empleado.objects.filter(
        estado_revision='Rechazado').order_by('-fecha_modificacion')

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
                    'message': 'Ya existe un aspirante con el número de documento ingresado.'}, status=400)

            if Empleado.objects.filter(correo_personal=data.get('correo_personal')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un aspirante con el correo personal ingresado.'}, status=400)

            # Instanciar ForeignKeys
            fk_ultimo_nivel_estudio_ins = NivelAcademico.objects.get(id=data.get('fk_ultimo_nivel_estudio'))
            fk_afp_ins = AFP.objects.get(id=data.get('fk_afp'))
            fk_departamento_residencia_ins = Departamento.objects.get(id=data.get('fk_departamento_residencia'))
            fk_sede_donde_labora_ins = Sede.objects.get(id=data.get('fk_sede_donde_labora'))

            nuevo_usuario = Empleado.objects.create(
                # Campos obligatorios
                fk_rol_id= data.get('fk_rol'),
                fk_tipo_documento_id=data.get('fk_tipo_documento'),
                cargo=data.get('cargo'),
                primer_nombre=data.get('primer_nombre'),
                primer_apellido=data.get('primer_apellido'),
                numero_documento=data.get('numero_documento'),
                correo_personal=data.get('correo_personal'),
                estado_revision=data.get('estado_revision'),
                # Campos opcionales
                segundo_nombre=data.get('segundo_nombre'),
                segundo_apellido=data.get('segundo_apellido'),
                fecha_nacimiento=data.get('fecha_nacimiento'),
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
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)

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
                    'message': 'Ya existe un empleado con el número de documento ingresado.'}, status=400)

            # Verificar si ya existe un usuario con el correo
            if Empleado.objects.filter(correo_personal=data.get('correo_personal')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un empleado con el correo personal ingresado.'}, status=400)

            # Instanciar ForeignKeys
            fk_ultimo_nivel_estudio_ins = NivelAcademico.objects.get(id=data.get('fk_ultimo_nivel_estudio_emp'))
            fk_afp_ins = AFP.objects.get(id=data.get('fk_afp_emp'))
            fk_arl_ins = ARL.objects.get(id=data.get('fk_arl_emp'))
            fk_caja_compensacion_ins = CajaCompensacion.objects.get(id=data.get('fk_caja_compensacion_emp'))
            fk_departamento_residencia_ins = Departamento.objects.get(id=data.get('fk_departamento_residencia_emp'))
            fk_sede_donde_labora_ins = Sede.objects.get(id=data.get('fk_sede_donde_labora_emp'))

            nuevo_usuario = Empleado.objects.create(
                # Campos obligatorios
                fk_rol_id= data.get('fk_rol_emp'),
                fk_tipo_documento_id=data.get('fk_tipo_documento_emp'),
                cargo=data.get('cargo_emp'),
                primer_nombre=data.get('primer_nombre_emp'),
                primer_apellido=data.get('primer_apellido_emp'),
                numero_documento=data.get('numero_documento_emp'),
                correo_personal=data.get('correo_personal_emp'),
                estado_revision=data.get('estado_revision_emp'),
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
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido.'
        }, status=405)


@login_required
@csrf_exempt
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
                return JsonResponse({"status": "error", "message": "El código IES debe ser numérico."})
            if codigo_pais and not codigo_pais.isdigit():
                return JsonResponse({"status": "error", "message": "El código del país debe ser numérico."})

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
            print(e)
            return JsonResponse({
                "status": "error",
                "message": 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Método no permitido."
    }, status=405)


@login_required
@csrf_exempt
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
            print(e)
            return JsonResponse({
                "status": "error",
                "message": 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Método no permitido."
    }, status=405)


#
# ---------------------------- VISTA EMPLEADOS ---------------------------------
#


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
    empleados_activos = Empleado.objects.filter(activo=True, estado_revision='Contratado').order_by('-fecha_modificacion')
    # Término de búsqueda para aspirantes en estado 'Rechazado'
    empleado_inactivo = request.GET.get('empleado_inactivo', '').strip()
    empleados_inactivos = Empleado.objects.filter(activo=False, estado_revision='Contratado').order_by('-fecha_modificacion')

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


# Falta configurar 🚫
@login_required
@csrf_exempt
def cargar_empleados_masivamente(request):
    # if request.method == 'POST' and 'archivoExcel' in request.FILES:
    #     archivo = request.FILES['archivoExcel']
    #     try:
    #         # Leer el archivo Excel usando pandas
    #         import pandas as pd
    #         datos = pd.read_excel(archivo)

    #         # Validar que las columnas requeridas existan en el archivo
    #         columnas_requeridas = [
    #             'primer_nombre', 'primer_apellido', 'fk_rol', 'cargo',
    #             'fecha_nacimiento', 'fk_tipo_documento', 'numero_documento',
    #             'correo_personal', 'celular', 'departamento_residencia',
    #             'ultimo_nivel_estudio', 'eps', 'afp'
    #         ]
    #         if not all(col in datos.columns for col in columnas_requeridas):
    #             return JsonResponse({
    #                 'status': 'error',
    #                 'message': f"El archivo debe contener las columnas: {', '.join(columnas_requeridas)}"
    #             }, status=400)

    #         # Validar que todos los roles en el Excel existen
    #         roles_no_encontrados = set(
    #             datos['fk_rol']) - set(Rol.objects.values_list('descripcion', flat=True))
    #         if roles_no_encontrados:
    #             return JsonResponse({
    #                 'status': 'error',
    #                 'message': f"Los siguientes roles no existen en la base de datos: {', '.join(roles_no_encontrados)}"
    #             }, status=400)

    #         # Iterar sobre las filas del archivo y crear empleados
    #         for _, fila in datos.iterrows():
    #             try:
    #                 # Validar que el rol existe
    #                 rol = Rol.objects.get(descripcion=fila['fk_rol'])
    #                 tipo_documento = TipoDocumento.objects.get(
    #                     descripcion=fila['fk_tipo_documento'])

    #                 # Crear o actualizar el usuario
    #                 Empleado.objects.update_or_create(
    #                     numero_documento=fila['numero_documento'],
    #                     defaults={
    #                         'primer_nombre': fila['primer_nombre'],
    #                         'primer_apellido': fila['primer_apellido'],
    #                         'fk_rol': rol,
    #                         'cargo': fila['cargo'],
    #                         'fecha_nacimiento': fila['fecha_nacimiento'],
    #                         'fk_tipo_documento': tipo_documento,
    #                         'correo_personal': fila['correo_personal'],
    #                         'celular': fila['celular'],
    #                         'departamento_residencia': fila['departamento_residencia'],
    #                         'ultimo_nivel_estudio': fila['ultimo_nivel_estudio'],
    #                         'eps': fila['eps'],
    #                         'afp': fila['afp'],
    #                         'estado_revision': 'Contratado',
    #                         'activo': True,
    #                         'fk_creado_por': request.user
    #                     }
    #                 )
    #             except Rol.DoesNotExist:
    #                 return JsonResponse({
    #                     'status': 'error',
    #                     'message': f"Error al procesar la fila con documento {fila['numero_documento']}: Rol '{fila['fk_rol']}' no encontrado. Verifica que el rol exista en la base de datos."
    #                 }, status=400)
    #             except TipoDocumento.DoesNotExist:
    #                 return JsonResponse({
    #                     'status': 'error',
    #                     'message': f"Error al procesar la fila con documento {fila['numero_documento']}: Tipo de Documento '{fila['fk_tipo_documento']}' no encontrado. Verifica que exista en la base de datos."
    #                 }, status=400)

    #         return JsonResponse({
    #             'status': 'success',
    #             'message': 'Carga masiva realizada con éxito.'
    #         }, status=200)
    #     except Exception as e:
    #         print(e)
    #         return JsonResponse({
    #             'status': 'error',
    #             'message': 'Error inesperado. Por favor, intente nuevamente.'
    #         }, status=500)

    # return JsonResponse({
    #     'status': 'error',
    #     'message': 'Método no permitido.'
    # }, status=405)
    pass


#
# ---------------------------- FUNCIONES PARA VISTAS ASPIRANTES Y EMPLEADOS ---------------------------------
#


@login_required
def detalle_usuario(request, tipo, usuario_id):
    """
    Muestra los detalles de un aspirante o empleado según el tipo y el estado del usuario.
    """
    usuario = get_object_or_404(Empleado, id=usuario_id)
    if usuario:
        template = "partials/detalle_usuario.html"
        detalles_academicos = DetalleAcademico.objects.filter(usuario=usuario)
        detalles_laborales = DetalleExperienciaLaboral.objects.filter(usuario=usuario)
    else:
        return HttpResponseNotFound("No se puede mostrar la información solicitada.")

    return render(request, template, {
        "usuario": usuario,
        "detalles_academicos": detalles_academicos,
        "detalles_laborales": detalles_laborales,
    })


@login_required
@csrf_exempt
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
@csrf_exempt
def definir_contrato(request, tipo, usuario_id):
    """
    Muestra el formulario para definir el contrato de un empleado.
    """
    usuario = get_object_or_404(Empleado, id=usuario_id)

    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    # Obtener el listado de tipos de contratos
    tipos_contrato = TipoContrato.objects.all()

    # Obtener el contrato más reciente del usuario (si existe)
    contrato = Contrato.objects.filter(fk_usuario=usuario).order_by('-fecha_inicio').first()

    contexto.update({
        "usuario": usuario,
        "tipo": tipo,
        "tipos_contrato_list": tipos_contrato,
        "contrato_usuario": contrato # Pasamos un solo contrato, no una queryset
    })

    return render(
        request,
        "partials/detalle_contrato.html",
        contexto,
    )


@login_required
def definir_contrato_usuario(request, tipo, usuario_id):
    """
    Muestra el formulario para definir el contrato de un empleado.
    """
    usuario = get_object_or_404(Empleado, id=usuario_id)
    data = request.POST
    try:
        print(usuario, data)
        return JsonResponse({
            "status": "success",
            "message": "Contrato guardado correctamente.",
        })
    except Exception as e:
        print(e)
        return JsonResponse({
            "status": "error",
            "message": 'Error inesperado. Por favor, intente nuevamente.'
        }, status=500)

# Falta configurar 🚫
def calcular_dias_laborados_por_contrato(fecha_inicio, fecha_final):
    """Calcula los días laborados durante todo el contrato."""
    fecha_inicio = datetime.strptime(str(fecha_inicio), "%Y-%m-%d")
    fecha_final = datetime.strptime(str(fecha_final), "%Y-%m-%d")

    dias_laborados = (fecha_final - fecha_inicio).days + 1
    return dias_laborados if dias_laborados > 0 else 0


def calcular_dias_laborados_por_mes(fecha_inicio, fecha_final):
    """Calcula los días laborados en cada mes del contrato, con un máximo de 30 días por mes."""
    fecha_inicio = datetime.strptime(str(fecha_inicio), "%Y-%m-%d")
    fecha_final = datetime.strptime(str(fecha_final), "%Y-%m-%d")

    dias_laborados_por_mes = {}
    fecha_actual = fecha_inicio

    while fecha_actual <= fecha_final:
        year = fecha_actual.year
        month = fecha_actual.month
        inicio_mes = fecha_actual.replace(day=1)
        fin_mes = min((inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1), fecha_final)

        dias_laborales_mes = 30
        dias_trabajados = min((fin_mes - fecha_actual).days + 1, dias_laborales_mes - (fecha_actual.day - 1))
        clave_mes = f"{year}-{month:02d}"
        dias_laborados_por_mes[clave_mes] = dias_trabajados

        fecha_actual = fin_mes + timedelta(days=1)

    return dias_laborados_por_mes

# Falta configurar 🚫
def generar_detalles_contrato(contrato):
    """Genera registros de detalles del contrato con días laborados y valores a pagar por mes."""
    fecha_inicio = contrato.fecha_inicio
    fecha_fin = contrato.fecha_fin
    valor_mensual = contrato.valor_contrato

    # Validar que los campos necesarios no sean None
    if not fecha_inicio or not fecha_fin or valor_mensual is None:
        raise ValueError("El contrato debe tener fecha de inicio, fecha de fin y un valor mensual válido.")

    valor_mensual = Decimal(valor_mensual)  # Convertir a Decimal
    # Eliminar detalles previos
    DetalleContratro.objects.filter(fk_contrato=contrato).delete()

    # Obtener días laborados por mes
    dias_laborados_por_mes = calcular_dias_laborados_por_mes(fecha_inicio, fecha_fin)
    valor_dia = valor_mensual / 30  # Se asume un mes estándar de 30 días
    total_pagado = Decimal(0)

    detalles = []
    for mes, dias in dias_laborados_por_mes.items():
        valor_mes = round(dias * valor_dia, 2)
        total_pagado += valor_mes
        detalles.append(
            DetalleContratro(
                fk_contrato=contrato,
                mes_a_pagar=mes,
                dias_laborados=dias,
                valor_a_pagar=valor_mes,
            )
        )

    DetalleContratro.objects.bulk_create(detalles)
    return total_pagado

# Falta configurar 🚫
@login_required
def contrato_usuario(request, tipo, usuario_id):
    usuario = get_object_or_404(Empleado, id=usuario_id)
    data = request.POST

    tipo_contrato = data.get("tipo_contrato")
    fk_tipo_contrato = TipoContrato.objects.get(id=tipo_contrato)

    # dias_laborados = calcular_dias_laborados_por_contrato(fecha_inicio_contrato, fecha_fin_contrato)

    try:
        contrato, created = Contrato.objects.get_or_create(
            fk_usuario=usuario,
            defaults={
                # "fecha_inicio": fecha_inicio_contrato,
                # "fecha_fin": fecha_fin_contrato,
                "fk_tipo_contrato": fk_tipo_contrato,
                "dedicacion": data.get("dedicacion"),
                "valor_contrato": data.get("valor_contrato"),
                # "total_dias_laborados": dias_laborados,
                "vigencia_contrato": True,
            },
        )

        if not created:
            # contrato.fecha_inicio = fecha_inicio_contrato
            # contrato.fecha_fin = fecha_fin_contrato
            contrato.fk_tipo_contrato = fk_tipo_contrato
            contrato.dedicacion = data.get("dedicacion")
            contrato.valor_contrato = data.get("valor_contrato")
            # contrato.total_dias_laborados = dias_laborados
            contrato.vigencia_contrato = True
            contrato.save()

        # Solo generar detalles si el valor del contrato está definido
        if contrato.valor_contrato:
            total_pagado = generar_detalles_contrato(contrato)
        else:
            total_pagado = None

        return JsonResponse({
            "status": "success",
            "message": "Contrato y detalles creados/actualizados correctamente.",
            "valor_total_pagado": float(total_pagado) if total_pagado else None,
        })

    except IntegrityError:
        return JsonResponse({
            "status": "error",
            "message": "Error de integridad al crear/actualizar el contrato."
        }, status=400,)
    except ValueError as e:
        print(e)
        return JsonResponse({
            "status": "error",
            "message": 'Error inesperado. Por favor, intente nuevamente.'
        }, status=405)
    except Exception as e:
        print(e)
        return JsonResponse({
            "status": "error",
            "message": 'Error inesperado. Por favor, intente nuevamente.'
        }, status=500)



@login_required
def actualizar_usuario(request, tipo, usuario_id):
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
            usuario.estado_revision = request.POST.get("estado_revision", usuario.estado_revision)

            # Campos opcionales
            usuario.segundo_nombre = request.POST.get("segundo_nombre", usuario.segundo_nombre)
            usuario.segundo_apellido = request.POST.get("segundo_apellido", usuario.segundo_apellido)
            usuario.fecha_nacimiento = request.POST.get("fecha_nacimiento", usuario.fecha_nacimiento)
            usuario.lugar_nacimiento = request.POST.get("lugar_nacimiento", usuario.lugar_nacimiento)
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
                usuario.fk_departamento_residencia = EPS.objects.get(id=departamento_residencia_id)
            usuario.ciudad_residencia = request.POST.get("ciudad_residencia", usuario.ciudad_residencia)
            usuario.barrio_residencia = request.POST.get("barrio_residencia", usuario.barrio_residencia)
            if sede_donde_labora_id := request.POST.get("fk_sede_donde_labora"):
                usuario.fk_sede_donde_labora = Sede.objects.get(id=sede_donde_labora_id)
            usuario.url_hoja_de_vida = request.POST.get("url_hoja_de_vida", usuario.url_hoja_de_vida)

            # Cambiar el estado de activo según el estado de revisión
            if usuario.estado_revision == "Contratado":
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


#
# ----------------------------  VISTA FUNCIONES SUSTANTIVAS ---------------------------------
#

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
# ----------------------------  VISTA CONTABILIDAD ---------------------------------
#

def gestion_docentes(request):
    """
    Muestra la gestión de contratos
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    dia_actual = datetime.now().date()
    
    contexto.update ({
        'programa_list': Programa.objects.all(),
    })

    return render(request, 'docentes.html', contexto)


def gestion_administrativos(request):
    """
    Muestra la gestión de administrativos.
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    # Filtrar usuarios con rol de administrativo
    administrativos = Empleado.objects.filter(fk_rol__descripcion="Administrativo").order_by('-fecha_modificacion')

    # Agregar los administrativos al contexto
    contexto.update({
        "administrativos": administrativos,
        "dia_actual": datetime.now().date(),
    })

    return render(request, 'administrativos.html', contexto)


#
# ----------------------------  VISTA CARGA ACADEMICA ---------------------------------
#


def calcular_dias_laborados_docentes(fecha_inicio, fecha_fin):

    pass


@login_required
def gestion_carga_academica(request):
    """
    Muestra la gestión de carga académica, filtrando los semestres según el programa del usuario.
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    dia_actual = datetime.now().date()

    # Agrupar cargas académicas por semestre
    cargas_dict = defaultdict(list)
    for carga in contexto["cargas_academicas"]:
        cargas_dict[carga.fk_semestre.semestre].append(carga)

    # Convertir a diccionario normal para el template
    contexto["cargas_dict"] = dict(cargas_dict)

    contexto.update({
            "dia_actual": dia_actual,
        })

    return render(request, 'carga_academica.html', contexto)


#
# ----------------------------  VISTA MATRIZ DOCENTES ---------------------------------
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
def obtener_dedicacion_docente(request, docente_id):
    """
    Obtiene la dedicación del docente según su ID.
    """
    try:
        contrato = Contrato.objects.filter(fk_usuario_id=docente_id, vigencia_contrato = True).first()
        if contrato:
            # Si el contrato existe, obtener la dedicación
            dedicacion = contrato.dedicacion
            return JsonResponse({
                'status': 'success',
                'dedicacion': dedicacion
            })
        else:
            # Si no hay contrato, devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontró un contrato activo para el docente.'
            }, status=404)
    except Empleado.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Docente no encontrado.'
        }, status=404)
    except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': 'Error inesperado. Por favor, intente nuevamente.'
            }, status=500)


def calcular_valor_a_pagar(horas_semanales, total_horas, fk_docente_asignado):
    """
    Calcula el valor a pagar según las horas semanales y el total de horas.
    """
    ultimo_nivel_estudio = Empleado.objects.get(id=fk_docente_asignado).fk_ultimo_nivel_estudio
    return

@login_required
@csrf_exempt
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

                # Guardar los datos en la DB
                CargaAcademica.objects.create(
                    fk_periodo = fk_periodo_inst,
                    fk_programa = fk_programa_inst,
                    fk_semestre = fk_semestre_inst,
                    fk_materia = fk_materia_inst,
                    fk_docente_asignado = fk_docente_asignado_inst,
                    horas_semanales = carga["horas_semanales"],
                    total_horas = carga["total_horas"],
                    materia_compartida = carga["materia_compartida"],
                    # fk_creado_por = request.user,
                    fecha_creacion = datetime.now(),

                    # valor_a_pagar = calcular_valor_a_pagar(
                    #     carga["horas_semanales"],
                    #     carga["total_horas"],
                    #     carga["fk_docente_asignado"]
                    # )
                )
            return JsonResponse({
                'status': 'success',
                'message': 'Carga académica agregada correctamente.'})
        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Error al agregar la carga académica. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': f"Error inesperado: {e}"
            }, status=500)















































#
# ---------------------------- VISTA REPORTES ---------------------------------
#


@login_required
def reportes(request):
    contexto = obtener_db_info(request)

    # Capturar parámetros del request
    fecha_creacion = request.GET.get('fecha_creacion')
    estado = request.GET.get('estado')
    activo = request.GET.get('activo')  # Nuevo filtro
    page = request.GET.get('page', 1)  # Página actual, por defecto 1

    # Validar formato de fecha
    if fecha_creacion:
        fecha_creacion = parse_date(fecha_creacion)
        if not fecha_creacion:
            fecha_creacion = None

    # Filtrar datos según los parámetros
    usuarios = Empleado.objects.all()
    if fecha_creacion:
        usuarios = usuarios.filter(fecha_creacion__date=fecha_creacion)

    # Filtrar por estado
    if estado:
        usuarios = usuarios.filter(estado_revision=estado)

    # Filtrar por activo/inactivo
    if activo:
        if activo == "Activo":
            usuarios = usuarios.filter(activo=True)
        elif activo == "Inactivo":
            usuarios = usuarios.filter(activo=False)

    # Paginación: 25 registros por página
    paginator = Paginator(usuarios, 25)
    page_obj = paginator.get_page(page)

    # Actualizar el contexto con la paginación y filtros
    contexto.update({
        'page_obj': page_obj,
        'fecha_creacion': request.GET.get('fecha_creacion', ''),
        'estado': request.GET.get('estado', ''),
        'activo': request.GET.get('activo', '')  # Nuevo campo en el contexto
    })

    return render(request, 'reportes.html', contexto)


@login_required
def generar_reporte_excel(request):
    # Capturar filtros de la URL
    fecha_creacion = request.GET.get('fecha_creacion')
    estado = request.GET.get('estado')

    # Configuración de la zona horaria local
    zona_horaria_local = pytz.timezone('America/Bogota')

    # Filtrar datos según los parámetros enviados
    usuarios = Empleado.objects.all()
    if fecha_creacion:
        try:
            # Convertir la fecha a rango con zona horaria local
            fecha_inicio = zona_horaria_local.localize(datetime.strptime(fecha_creacion, "%Y-%m-%d"))
            fecha_fin = fecha_inicio + timedelta(days=1)
            usuarios = usuarios.filter(fecha_creacion__gte=fecha_inicio, fecha_creacion__lt=fecha_fin)
        except ValueError:
            fecha_creacion = None

    if estado:
        usuarios = usuarios.filter(estado_revision=estado)

    # Crear libro de Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Reporte SNIES"

    # Encabezados
    sheet.append(["ID", "Nombre Completo", "Cargo", "Número Documento", "Correo", "Estado", "Fecha Creación"])

    # Insertar datos filtrados
    for idx, usuario in enumerate(usuarios, start=1):
        fecha_local = usuario.fecha_creacion.astimezone(zona_horaria_local)
        sheet.append([
            idx,
            f"{usuario.primer_nombre} {usuario.primer_apellido}",
            usuario.cargo,
            usuario.numero_documento,
            usuario.correo_personal,
            usuario.estado_revision,
            # Mostrar en la zona local
            fecha_local.strftime("%d-%m-%Y %H:%M:%S")
        ])

    # Generar nombre de archivo personalizado
    nombre_archivo = f"reporte_snies_{
        fecha_creacion}.xlsx" if fecha_creacion else "reporte_snies.xlsx"

    # Respuesta HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="{
        nombre_archivo}"'
    workbook.save(response)
    return response


#
# ---------------------------- GENERAR CONTRATOS ---------------------------------
#

@login_required
def generar_contrato_word(request, usuario_id):
    """
    Genera un contrato en formato Word para el usuario especificado y lo devuelve como archivo descargable.
    """
    # Obtener el usuario y su contrato
    usuario = get_object_or_404(Empleado, id=usuario_id)
    contrato = Contrato.objects.filter(fk_usuario=usuario).order_by('-fecha_inicio').first()

    # Verificar si el usuario tiene un contrato y está en estado "Contratado"
    if not contrato or usuario.estado_revision != "Contratado":
        return JsonResponse({
            'status': 'error',
            'message': 'El usuario no tiene un contrato asociado o no está en estado "Contratado".'
        }, status=400)

    # Crear un nuevo documento Word
    doc = Document()

    header = doc.sections[0].header
    header_paragraph = header.paragraphs[0]

    run = header_paragraph.add_run()
    run.add_picture('home/static/images/logo_unicorsalud.png', width=Inches(3))

    # Título del contrato
    doc.add_heading('CONTRATO A TÉRMINO FIJO INFERIOR A UN AÑO', level=1).alignment = 1  # Centrado

    # Tabla inicial con los datos del trabajador
    table = doc.add_table(rows=10, cols=2)
    table.style = 'Table Grid'

    # Rellenar la tabla con los datos
    table.cell(0, 0).text = "NOMBRE DEL TRABAJADOR"
    table.cell(0, 1).text = f"{usuario.primer_nombre} {usuario.segundo_nombre or ''} {usuario.primer_apellido} {usuario.segundo_apellido or ''}"
    table.cell(1, 0).text = "NACIONALIDAD"
    table.cell(1, 1).text = "COLOMBIANA"
    table.cell(2, 0).text = "LUGAR DONDE DESEMPEÑA SUS LABORES"
    table.cell(2, 1).text = "BARRANQUILLA"
    table.cell(3, 0).text = "CARGO"
    table.cell(3, 1).text = usuario.cargo or "N/A"
    table.cell(4, 0).text = "SALARIO MENSUAL"
    table.cell(4, 1).text = f"${contrato.valor_contrato:,}" if contrato.valor_contrato else "N/A"
    table.cell(5, 0).text = "AUXILIO DE TRANSPORTE"
    table.cell(5, 1).text = "$200,000"  # Valor fijo según la plantilla
    table.cell(6, 0).text = "TOTAL SALARIO"
    table.cell(6, 1).text = f"${contrato.valor_contrato + 200000:,}" if contrato.valor_contrato else "N/A"
    table.cell(7, 0).text = "FECHA INICIO CONTRATO"
    table.cell(7, 1).text = contrato.fecha_inicio.strftime("%d/%m/%Y") if contrato.fecha_inicio else "N/A"
    table.cell(8, 0).text = "FECHA FINALIZACION CONTRATO"
    table.cell(8, 1).text = contrato.fecha_fin.strftime("%d/%m/%Y") if contrato.fecha_fin else "N/A"

    # Ajustar el estilo de la tabla
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(12)

    # Agregar el contenido del contrato (cláusulas)
    doc.add_paragraph(
        "Entre la CORPORACIÓN UNIVERSITARIA DE CIENCIAS EMPRESARIALES, EDUCACIÓN Y SALUD –UNICORSALUD- identificada con NIT. No. 800.248.926-2, Institución de Educación Superior sin ánimo de lucro con Personería Jurídica No. 03514 de 15 de Julio/93 y Resolución No 3597 de 30 de junio/06 expedida por el Ministerio de Educación Nacional y quien en este CONTRATO se denominará la CORPORACIÓN y "
        f"{usuario.primer_nombre} {usuario.segundo_nombre or ''} {usuario.primer_apellido} {usuario.segundo_apellido or ''}, también mayor de edad con domicilio en la ciudad de BARRANQUILLA, identificado(a) con la cédula de ciudadanía No. {usuario.numero_documento}, quien para estos efectos se denominará EL TRABAJADOR, se ha celebrado el contrato de trabajo a término fijo regido por las siguientes cláusulas:"
    )

    # Cláusula Primera: Objeto
    doc.add_heading("PRIMERA: OBJETO.", level=2)
    doc.add_paragraph(
        "LA CORPORACION, contrata los servicios especiales del TRABAJADOR y éste se obliga: a) A poner al servicio de la CORPORACION toda su capacidad normal de trabajo en el desempeño de las funciones propias del oficio mencionado y en las labores anexas y complementarias del mismo, de conformidad con las órdenes e instrucciones que le imparta la CORPORACION directamente o a través de sus representantes. b) Prestar sus servicios en forma personal en el horario contratado con LA CORPORACION; es decir, a no prestar directamente servicios laborales a otros EMPLEADORES, durante el cumplimiento del horario antes mencionado. y c) A guardar absoluta reserva sobre los hechos, documentos físicos y/o electrónicos, informaciones y en general, sobre todos los asuntos y materias que lleguen a su conocimiento por causa o por ocasión de su contrato de trabajo, EL TRABAJADOR se compromete a aceptar cambio de empleo o funciones a donde se le promueva dentro de las distintas dependencias que la Institución tiene o estableciere, siempre que el cambio no desmejore sus condiciones laborales ni de remuneración del trabajador. Mientras la CORPORACION no resuelva otra cosa los servicios serán prestados en la ciudad de BARRANQUILLA, siendo de advertir que ha sido contratado en la misma ciudad."
    )

    # Cláusula Segunda: Remuneración
    doc.add_heading("SEGUNDA: REMUNERACIÓN.", level=2)
    doc.add_paragraph(
        f"LA CORPORACION pagará al trabajador por la prestación de sus servicios, un salario mensual por ${contrato.valor_contrato:,} incluyendo el auxilio de transporte legal vigente siempre y cuando le aplique, se le realizará el descuento correspondiente a la seguridad social (salud y pensión), el salario se cancela por mes vencido y será depositado en una cuenta bancaria individual de nómina, así mismo; se establece que el pago de las prestaciones sociales y demás derechos derivados del contrato de trabajo se efectuará mediante transferencia a la respectiva cuenta de nómina al finalizar este contrato."
    )

    # Cláusula Tercera: Pagos No Salariales
    doc.add_heading("TERCERA: PAGOS NO SALARIALES.", level=2)
    doc.add_paragraph(
        "Las partes de común acuerdo y de conformidad con lo establecido en los artículos 15 y 16 de la Ley 50 de 1990, en concordancia con lo señalado en el artículo 17 de la Ley 344 de 1996, determinan que las sumas que ocasionalmente y por mera liberalidad reciba de la CORPORACION no tendrán naturaleza salarial y/o prestacional, conforme lo señalado en el artículo 128 del Código Sustantivo de Trabajo y por lo tanto no se tendrán en cuenta como factor salarial para la liquidación de acreencias laborales, ni el pago de aportes en seguridad social."
    )

    # Cláusula Cuarta: Trabajo Nocturno, Suplementario, Dominical y/o Festivo
    doc.add_heading("CUARTA: TRABAJO NOCTURNO, SUPLEMENTARIO, DOMINICAL Y/O FESTIVO.", level=2)
    doc.add_paragraph(
        "Todo trabajo nocturno, suplementario o en horas extras y todo trabajo en domingo o festivo en los que legalmente debe concederse descanso, se remunera conforme lo dispone expresamente la ley, salvo acuerdo en contrario entre las partes o en pacto colectivo o fallo arbitral. Para el reconocimiento y pago del trabajo suplementario, nocturno, dominical o festivo, LA CORPORACION o sus representantes deberán haberlo autorizado previamente y por escrito. Cuando la necesidad de este trabajo se presente de manera imprevista e inaplazable, deberá ejecutarse y darse cuenta de él por escrito, a la mayor brevedad, a LA CORPORACION o a sus representantes para su aprobación. LA CORPORACION, en consecuencia, no reconocerá ningún trabajo suplementario, trabajo nocturno o en días de descanso obligatorio que no haya sido autorizado previamente o que, habiendo sido avisado inmediatamente, no haya sido aprobada como anteriormente se expuso. Tratándose de trabajadores de dirección, confianza o manejo, no habrá lugar al pago de horas extras, conforme lo dispuesto en el artículo 162 del Código Sustantivo del Trabajo."
    )

    # Cláusula Quinta: Duración del Contrato
    doc.add_heading("QUINTA: DURACION DEL CONTRATO.", level=2)
    doc.add_paragraph(
        "El término inicial de duración del contrato será el señalado en la parte superior del documento, respecto del pago de sus prestaciones sociales, se establece que en cumplimiento de lo previsto en el artículo 46 del C.S.T. modificado por el artículo 3° de la ley 50 de 1990, EL TRABAJADOR tendrá derecho al pago de sus prestaciones sociales en proporción al tiempo laborado, cualquiera que éste sea, cancelándose al finalizar el presente contrato."
    )

    # Cláusula Sexta: Jornada de Trabajo
    doc.add_heading("SEXTA: JORNADA DE TRABAJO.", level=2)
    doc.add_paragraph(
        "El TRABAJADOR salvo estipulación expresa y escrita en contrario, se obliga a laborar la jornada máxima legal, cumpliendo con los turnos y horarios que señale LA CORPORACION, quien podrá cambiarlos o ajustarlos cuando lo estime conveniente. Por el acuerdo expreso o tácito de las partes, podrán repartirse total o parcialmente las horas de la jornada ordinaria, con base en lo dispuesto por el artículo 164 del C.S.T. modificado por el artículo 23 de la ley 50 de 1990, teniendo en cuenta que los tiempos de descanso entre las secciones de la jornada no se computan dentro de la misma, según lo dispuesto en el artículo 167 del ordenamiento laboral. De igual manera, las partes acuerdan desde la firma del presente contrato que se podrá prestar el servicio en los turnos de la jornada flexible contemplados en el artículo 51 de la ley 789 de 2002."
    )

    # Cláusula Séptima: Jornada de Trabajo Flexible
    doc.add_heading("SÉPTIMA: JORNADA DE TRABAJO FLEXIBLE.", level=2)
    doc.add_paragraph(
        "Las partes acuerdan que el TRABAJADOR laborará conforme lo permite la jornada flexible contenida en el artículo 51 de la Ley 789 de 2002, en una jornada máxima de cuarenta y ocho (48) horas durante seis (6) días de la semana en los turnos y horarios que LA CORPORACION determine unilateralmente y en forma anticipada, cuya duración diaria no podrá ser superior a cuatro (4) horas continuas, ni superior a diez (10) horas y sin que haya lugar al pago de cargos por trabajo extraordinario siempre y cuando no exceda el promedio de las cuarenta y ocho (48) horas semanales en la jornada laboral ordinaria de 06:00 a.m. a 9:00 p.m. Ley 1846 de 2017 y la reducción gradual a 42 horas de la jornada laboral sin que disminuya el salario, obedece a la Ley 2101 del 2021 y al artículo 161 del Código Sustantivo del Trabajo, el cual se modificó, este comenzaría a regir en julio de 2023 reduciendo una (1) hora de la jornada laboral semanal y reducir a cuarenta y siete (47) horas semanales y se extendería hasta el mismo mes del año 2026 para alcanzar la disminución de la jornada laboral a cuarenta y dos (42) horas semanales."
    )

    # Cláusula Octava: Período de Prueba
    doc.add_heading("OCTAVA: PERIODO DE PRUEBA.", level=2)
    doc.add_paragraph(
        "Las partes acuerdan un período de prueba no podrá ser superior a la quinta parte del término inicial de este contrato, en caso de prorroga se entenderá, que no hay nuevo periodo de prueba, por consiguiente durante este período tanto LA CORPORACION, como EL TRABAJADOR podrán terminar el contrato en forma unilateral, en cualquier tiempo, sin que se cause el pago de indemnización alguna, de conformidad con lo dispuesto en el artículo 80 del Código Sustantivo de Trabajo modificado por el Artículo 3° del Decreto 617 de 1954. En caso de prórrogas, se entenderá que no hay nuevo periodo de prueba, de acuerdo con lo dispuesto por el artículo 78 del C.S.T., modificado por el artículo 7º de la Ley 50 de 1990."
    )

    # Cláusula Novena: Terminación Unilateral
    doc.add_heading("NOVENA: TERMINACIÓN UNILATERAL.", level=2)
    doc.add_paragraph(
        "Son justas causas para dar por terminado unilateralmente este contrato, por cualquiera de las partes, las enumeradas en los artículos 62 y 63 del C.S.T. modificados por el artículo 7° del Decreto 2351 de 1965 y además, por parte de la CORPORACION, las faltas que para el efecto se califiquen como graves en el Reglamento Interno de Trabajo y demás reglamentos y documentos que contengan reglamentaciones, órdenes, instrucciones o prohibiciones de carácter general o particular, pactos. Expresamente se califican en este acto como faltas graves la violación a las obligaciones y prohibiciones contenidas en el mencionado Reglamento. Además de las previstas en la ley, se consideran justas causas graves para poner término a éste contrato, por parte de la CORPORACION, los siguientes hechos imputables al trabajador, aún ocurridos por primera vez: 1o) La violación de cualquiera de sus obligaciones legales, contractuales o reglamentarias; 2o) El incumplimiento del horario o la no asistencia al trabajo sin justa causa a juicio de la CORPORACION; 3o) El abandono o retiro del sitio de trabajo sin el debido permiso del superior inmediato; 4o) No atender en debida forma cualquier orden de la CORPORACION, relacionada con el presente contrato; 5o) Todo acto inmoral o delictuoso, toda falta de respeto, disciplina o lealtad, todo acto de violencia, injuria o malos tratamientos en que incurra el trabajador contra sus jefes, directivos o compañeros de trabajo; 6o) Cualquier acto grave en su vida privada que cometa fuera o dentro de las dependencias en que le corresponda laborar y que atente contra la naturaleza, fines o buen nombre de la CORPORACION; 7o) Todo daño material causado intencionalmente o por descuido a las edificaciones, instrumentos, elementos de la CORPORACION, o que pongan en grave peligro la seguridad de las personas; 8o) Llegar embriagado al sitio de trabajo o ingerir en éste bebidas embriagantes o en general, todo vicio que altere la disciplina y la buena marcha de la CORPORACION; 9o) Toda detención preventiva por más de treinta (30) días, o arresto correccional aún por tiempo menor, cuando la causa de la sanción sea grave y; 10o) El deficiente rendimiento en el desempeño de sus funciones. 11º) Fraude o intento de fraude en perjuicio de la Institución. 12º. Recibir dinero en efectivo o transferencia de los usuarios ya sea por concepto de derechos pecuniarios, matriculas, servicios o cualquier otro concepto. Por otra parte, se deja constancia a partir de la firma del presente documento que la fecha de terminación está señalada en la parte inicial del contrato, y por lo tanto no es necesaria nueva comunicación indicando dicha fecha y/o preaviso de vencimiento de contrato."
    )

    # Cláusula Décima: Políticas de Seguridad, Salud en el Trabajo y Medio Ambiente
    doc.add_heading("DECIMA: POLITICAS DE SEGURIDAD, SALUD EN EL TRABAJO Y MEDIO AMBIENTE.", level=2)
    doc.add_paragraph(
        "EL TRABAJADOR hace constar que recibe de la CORPORACION. Información del Sistema de Gestión de Seguridad y Salud en el Trabajo y los cuales declara conocer, así como del reglamento interno del trabajo, el cual se encuentra publicado. EL TRABAJADOR se obliga a cumplir las políticas y normas de Seguridad, Salud en el Trabajo, Medio Ambiente y Calidad cuando su labor la ejecute ejerciendo el objeto del presente contrato, se le aplicará procesos disciplinarios cuando EL TRABAJADOR con previo conocimiento realice actos inseguros en el sitio de trabajo, al igual que informar sobre las condiciones y seguimiento de su salud y se compromete que esta información suministrada es veraz. De lo contrario ameritará sanciones disciplinarias."
    )

    # Cláusula Décima Primera: Documentos e Información Confidencial y Reservada
    doc.add_heading("DÉCIMA PRIMERA: DOCUMENTOS E INFORMACIÓN CONFIDENCIAL Y RESERVADA.", level=2)
    doc.add_paragraph(
        "Sobre la base de considerar como confidencial y reservada toda información que EL TRABAJADOR reciba DE LA CORPORACION o de terceros en razón de su cargo, que incluye, pero sin que se limite a los elementos descritos, la información objeto de derecho de autor, patentes, técnicas, modelos, invenciones, procesos, algoritmos, programas ejecutables, investigaciones, detalles de diseño, información financiera, lista de clientes, inversionistas, trabajadores, estudiantes, notas, resultados de notas de evaluaciones antes que estas sean publicadas, relaciones de negocios y contractuales, pronósticos de negocios, planes de mercadeo y cualquier información revelada sobre terceras personas, salvo la que expresamente y por escrito se le manifieste que no tiene dicho carácter, o la que se tiene disponible para el público en general, EL TRABAJADOR se obliga a: a) Abstenerse de revelar o usar información relacionada con los trabajos o actividades que desarrolla LA CORPORACION, ni durante el tiempo de vigencia del contrato de trabajo, ni después de finalizado EL CONTRATO, se mantendrá la reserva de confidencialidad hasta por 2 años después de no estar activo en la CORPORACION, ya sea con terceras personas naturales o jurídicas, ni con personal de la misma CORPORACION, no autorizado para conocer información confidencial salvo autorización expresa DE LA CORPORACION. b) Entregar A LA CORPORACION cuando finalice el contrato de trabajo todos los archivos en original o copias con información confidencial que se encuentren en su poder, ya sea que se encuentre en documentos escritos, gráficos o archivos magnéticos como video, audio etc. c) En caso de violación de esta confidencialidad durante la vigencia del contrato de trabajo y los dos años posteriores a la terminación del mismo, las partes acuerdan expresamente que el incumplimiento de las disposiciones contenidas en el presente acuerdo es considerado como una falta grave y en tal sentido justa causa para la terminación del contrato de trabajo de conformidad con lo dispuesto en el literal a) numeral 6 del artículo 62 del C.S.T. subrogado por el artículo 7 del decreto 2351 de 1965. Lo anterior sin perjuicio de las acciones civiles, comerciales o penales que puedan instaurarse en contra del TRABAJADOR por parte de LA CORPORACION o de terceros como consecuencia de dicho incumplimiento."
    )

    # Cláusula Décima Segunda: Autorización de Descuentos
    doc.add_heading("DÉCIMA SEGUNDA: AUTORIZACIÓN DE DESCUENTOS.", level=2)
    doc.add_paragraph(
        "EL TRABAJADOR responderá por todos los elementos que se le confíen y en caso de pérdida, rotura, daño o deterioro de los mismos no imputables a su uso normal, pagará a la CORPORACION el valor comercial en el momento de la reposición de dichos bienes y a su vez el TRABAJADOR autoriza en forma expresa a la CORPORACION para retener, deducir y compensar de su salario y prestaciones si aquellos fueren insuficientes, cualquier suma de dinero que él llegara a adeudar por éstos conceptos y/o a cualquier título, como también si EL TRABAJADOR esté debiendo a la CORPORACION, por los siguientes conceptos: a) Préstamos debidamente autorizados por escrito. b) Valor de los elementos de trabajo y mercancías extraviadas y dañadas o deterioradas bajo su responsabilidad y que llegaran a faltar al momento de hacer entrega del inventario. c) Los valores que se le hubieran confiado para su manejo, y que hayan sido dispuestos abusivamente para otros propósitos en perjuicio de la CORPORACION. d) Los anticipos o sumas no legalizadas con las facturas o comprobantes requeridos que le fueron entregadas para gastos."
    )

    # Cláusula Décima Tercera: Obligaciones de la Corporación
    doc.add_heading("DECIMA TERCERA: OBLIGACIONES DE LA CORPORACION.", level=2)
    doc.add_paragraph(
        "Además de las obligaciones contenidas en el artículo 57 del Código Sustantivo de Trabajo, el EMPLEADOR se obliga a: a) Mantener al TRABAJADOR en las condiciones indicadas por la empresa al momento de aprobar la vacante b) Cumplir oportunamente las obligaciones de orden laboral asumidas con los contratados que correspondan de acuerdo con la naturaleza del servicio que presten. c) realizar la inducción y reinducción, d) socializar las políticas y dar a conocer el Programa y las responsabilidades del SG - SST d) Velar por el cumplimento de la normativa que se expida El Ministerio de Educación y Ministerio de Trabajo y por las disposiciones que regulen la relación laboral entre la CORPORACION y sus Trabajadores. De lo contrario ameritará sanciones disciplinarias."
    )

    # Cláusula Décima Cuarta: Modificación de las Condiciones Laborales
    doc.add_heading("DECIMA CUARTA: MODIFICACION DE LAS CONDICIONES LABORALES.", level=2)
    doc.add_paragraph(
        "EL TRABAJADOR acepta desde ahora expresamente todas las modificaciones de sus condiciones laborales determinadas por LA CORPORACION en ejercicio de su poder subordinante, tales como los turnos y jornadas de trabajo, el lugar de prestación de servicio, el cargo u oficio y/o funciones y la forma de remuneración, siempre que tales modificaciones no afecten su honor, dignidad o sus derechos mínimos, ni impliquen desmejoras sustanciales o graves perjuicios para él, de conformidad con lo dispuesto por el artículo 23 del C.S.T. modificado por el artículo 1° de la Ley 50 de 1990."
    )

    # Cláusula Décima Quinta: Dirección del Trabajador
    doc.add_heading("DECIMA QUINTA: DIRECCION DEL TRABAJADOR.", level=2)
    doc.add_paragraph(
        "EL TRABAJADOR para todos los efectos legales y en especial para la aplicación del parágrafo 1° del artículo 29 de la Ley 789 de 2002, norma que modificó el 65 del C.S.T., se compromete a informar por escrito y de manera inmediata a LA CORPORACION, cualquier cambio en su dirección de residencia, teniéndose en todo caso como suya, la última dirección registrada en su hoja de vida."
    )

    # Cláusula Décima Sexta: Tratamiento de Datos Personales
    doc.add_heading("DECIMA SEXTA: TRATAMIENTO DE DATOS PERSONALES.", level=2)
    doc.add_paragraph(
        "En cumplimiento a lo estipulado en la Ley 1581 de 2012 y demás normas y decretos que la complementan, el titular de datos personales autoriza para que la información suministrada en nuestras bases de datos sea utilizada exclusivamente por CORPORACIÓN UNIVERSITARIA DE CIENCIAS EMPRESARIALES, EDUCACIÓN Y SALUD - UNICORSALUD, para el desarrollo de diversos procedimientos relacionados directamente con su objeto social. Para más información lo invitamos a visitar nuestra Política de Privacidad en www.UNICORSALUD.edu.co/politicadeprivacidad, donde podrán conocer como ejercer sus derechos de acceder, rectificar, actualizar, suprimir los datos o revocar la autorización."
    )

    # Cláusula Décima Séptima: Efectos
    doc.add_heading("DECIMA SEPTIMA: EFECTOS.", level=2)
    doc.add_paragraph(
        "El presente contrato reemplaza en su integridad y deja sin efecto cualquiera otro contrato, verbal o escrito, celebrando entre las partes con anterioridad, pudiendo las partes convenir por escrito modificaciones al mismo, las que formaran parte integrante de este contrato."
    )

    # Firma
    doc.add_paragraph(
        f"En constancia se firma el presente documento en BARRANQUILLA, {datetime.now().strftime('%d/%m/%Y')}"
    )
    doc.add_paragraph("LA CORPORACION\n\n\n\n\nRepresentante Legal")
    doc.add_paragraph(f"EL TRABAJADOR\n\n\n\n\nC.C. {usuario.numero_documento}")

    # Guardar el documento en un buffer
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # Crear la respuesta HTTP para descargar el archivo
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="Contrato_{usuario.numero_documento}.docx"'
    return response


