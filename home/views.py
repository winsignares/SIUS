# Importar Librerias
from collections import defaultdict
from itertools import chain
import json
import traceback
from decimal import Decimal
from django.db.models import Sum, Value, Exists, OuterRef
from django.db.models.functions import Coalesce
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
from .models.talento_humano.usuarios import Empleado, EmpleadoUser, EstadoRevision
from .models.talento_humano.detalles_academicos import DetalleAcademico
from .models.talento_humano.detalles_exp_laboral import DetalleExperienciaLaboral
from .models.talento_humano.tipo_documentos import TipoDocumento
from .models.talento_humano.niveles_academicos import NivelAcademico, NivelAcademicoHistorico
from .models.talento_humano.datos_adicionales import EPS, AFP, ARL, Departamento, CajaCompensacion, Institucion, Sede
from .models.talento_humano.roles import Rol
from .models.talento_humano.contrato import TipoContrato, Contrato, DetalleContratro, Dedicacion
from .models.carga_academica import CargaAcademica, Materia, Periodo, Programa, ProgramaUser, Semestre, MateriaCompartida, FuncionesSustantivas


#
# ---------------------------- FUNCIONES EXTRAS ---------------------------------
#


# Revisado ✅
def error_404_view(request, exception):
    """
    Vista para manejar errores 404.
    """

    return render(request, '404.html', status=404)


# Revisado ✅
def obtener_db_info(request, incluir_datos_adicionales=False):
    """
        Función auxiliar para obtener información especifica del usuario autenticado.
        Además, se incluye el envío de datos de la base de dato si alguna otra función lo requiere.
    """
    usuario_autenticado = request.user
    grupos_usuario = usuario_autenticado.groups.values_list('name', flat=True)

    # Obtener el empleado vinculado a este usuario (puede haber varios; tomamos el primero)
    try:
        empleado_user = EmpleadoUser.objects.select_related('fk_empleado').filter(fk_user=usuario_autenticado).first()
        if empleado_user:
            usuario_log = empleado_user.fk_empleado
            usuario_log.primer_nombre = usuario_log.primer_nombre.capitalize()
            usuario_log.primer_apellido = usuario_log.primer_apellido.capitalize()
            usuario_log.cargo = usuario_log.cargo.upper()
        else:
            usuario_log = None
    except EmpleadoUser.DoesNotExist:
        usuario_log = None

    # Obtener el programa del usuario logueado
    programa_usuario_log = ProgramaUser.objects.filter(fk_user=usuario_autenticado.id).first()
    programa_usuario = programa_usuario_log.fk_programa if programa_usuario_log else None

    # Obtener el número de semestres del programa
    num_semestres = int(programa_usuario.numero_semestres) if programa_usuario else 0

    # Filtrar los semestres hasta el número del programa
    semestres_list = Semestre.objects.filter(id__lte=num_semestres).order_by("id")

    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    periodo_actual = Periodo.objects.filter(fecha_apertura__lte=fecha_actual, fecha_cierre__gte=fecha_actual).first()

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
            'horas_semanales',
            'fk_semestre_id'
        )

    # Obtener los docentes con contrato vigente en el periodo actual
    docentes = Empleado.objects.annotate(tiene_contrato=Exists(Contrato.objects.filter(fk_usuario=OuterRef('id'),fk_periodo_id=periodo_actual.id,vigencia_contrato=True))).filter(fk_rol_id__in=[2, 4],fk_estado_revision=1,activo=True,tiene_contrato=True).order_by('primer_nombre')
    docentes_con_dedicacion = []
    for docente in docentes:
        contrato = Contrato.objects.filter(fk_usuario=docente.id, fk_periodo_id=periodo_actual.id, vigencia_contrato=True).first()
        dedicacion_nombre_corto = contrato.fk_dedicacion.nombre_corto if contrato and contrato.fk_dedicacion else None
        # Crear un dict o puedes usar setattr en el objeto si quieres
        docente_dict = {
            'id': docente.id,
            'primer_nombre': docente.primer_nombre,
            'segundo_nombre': docente.segundo_nombre,
            'primer_apellido': docente.primer_apellido,
            'segundo_apellido': docente.segundo_apellido,
            'dedicacion': dedicacion_nombre_corto,
        }
        docentes_con_dedicacion.append(docente_dict)

    if programa_usuario and periodo_actual:
        cargas_academicas = CargaAcademica.objects.filter(
            fk_periodo_id=periodo_actual.id,
            fk_programa=programa_usuario.id
        ).order_by('id')
    else:
        cargas_academicas = CargaAcademica.objects.none()

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
            'roles_list': Rol.objects.filter(id__in=[2, 3, 4]),
            'instituciones_list': Institucion.objects.all().order_by('codigo'),
            'sedes_list': Sede.objects.all(),
            'semestres_list': semestres_list,
            'programas_list': list(programas),
            'materias_list_all': list(materias_list_all),
            'materias_list': list(materias_queryset),
            'periodos_list': Periodo.objects.all(),
            'docentes_list': docentes_con_dedicacion,
            'cargas_academicas': cargas_academicas,
            'periodo_actual': periodo_actual,
            'dedicacion_list': Dedicacion.objects.all(),
            'estado_revision_list': EstadoRevision.objects.all()
        })

    return contexto


#
# ---------------------------- INICIO DE SESIÓN ---------------------------------
#


# Revisado ✅
def iniciar_sesion_form(request):
    '''
        Función para mostrar el formulario de inicio de sesión.
    '''

    return render(request, 'login.html')


# Revisado ✅
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
                request,
                "El usuario ingresado no tiene una cuenta asociada.")
            return redirect('iniciar_sesion_form')

        user = authenticate(
            request,
            username=postEmail,
            password=postPsw
        )

        if user is None:
            messages.error(
                request,
                "La contraseña ingresada es incorrecta.")
            return render(request, 'login.html', {'email': postEmail})

        login(request, user)

        return redirect('dashboard')


#
# ---------------------------- REESTABLECER CONTRASEÑA ---------------------------------
#


# Revisado ✅
def restablecer_contraseña_form(request):
    '''
        Función para mostrar el formulario de restablecer contraseña.
    '''

    return render(request, 'restablecer_contraseña.html')


# Revisado ✅
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
                request,
                "El usuario ingresado no tiene una cuenta asociada.")
            return redirect('restablecer_contraseña_form')

        # Validar si las contraseñas coinciden
        if new_password != confirm_password:
            messages.error(
                request,
                "Las contraseñas no coinciden. Inténtalo nuevamente.")
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


# Revisado ✅
@login_required
def dashboard(request):
    '''
        Función para mostrar el dashboard cuando un usuario inicia sesión.
    '''
    contexto = obtener_db_info(request)

    return render(request, 'dashboard.html', contexto)


# Revisado ✅
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

# Revisado ✅
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


# Revisado ✅
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


# Revisado ✅
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


#
# ---------------------------- VISTA EMPLEADOS ---------------------------------
#


# Revisado ✅
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


#
# ---------------------------- FUNCIONES PARA VISTAS ASPIRANTES Y EMPLEADOS ---------------------------------
#


# Revisado ✅
@login_required
def detalle_usuario(request, usuario_id):
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


# Revisado ✅
@login_required
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


# Revisado ✅
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


# Revisado ✅
# def calcular_dias_laborados_por_contrato(fecha_inicio, fecha_final):
#     """
#     Calcula los días laborados durante todo el contrato, considerando meses de 30 días.
#     """
#     fecha_inicio = datetime.strptime(str(fecha_inicio), "%Y-%m-%d")
#     fecha_final = datetime.strptime(str(fecha_final), "%Y-%m-%d")

#     # Calcular meses completos y días restantes
#     meses = (fecha_final.year - fecha_inicio.year) * 12 + (fecha_final.month - fecha_inicio.month)
#     dias = fecha_final.day - fecha_inicio.day + 1

#     if dias < 0:
#         meses -= 1
#         dias += 30  # Siempre sumamos 30 días, no los reales del mes

#     dias_laborados = meses * 30 + dias
#     return dias_laborados if dias_laborados > 0 else 0


# Revisado ✅
# def calcular_dias_laborados_por_mes(fecha_inicio, fecha_final):
#     """
#     Calcula los días laborados en cada mes del contrato, con un máximo de 30 días por mes.
#     """
#     dias_laborados_por_mes = {}
#     fecha_actual = fecha_inicio

#     while fecha_actual <= fecha_final:
#         year = fecha_actual.year
#         month = fecha_actual.month
#         clave_mes = f"{year}-{month:02d}"

#         # Calcular el primer y último día a considerar en este mes
#         if fecha_actual.year == fecha_inicio.year and fecha_actual.month == fecha_inicio.month:
#             dia_inicio = fecha_actual.day
#         else:
#             dia_inicio = 1

#         if fecha_actual.year == fecha_final.year and fecha_actual.month == fecha_final.month:
#             dia_fin = fecha_final.day
#         else:
#             dia_fin = 30  # Siempre 30 días por mes

#         dias_trabajados = dia_fin - dia_inicio + 1
#         dias_laborados_por_mes[clave_mes] = dias_trabajados

#         # Avanzar al siguiente mes
#         if month == 12:
#             fecha_actual = fecha_actual.replace(year=year + 1, month=1, day=1)
#         else:
#             fecha_actual = fecha_actual.replace(month=month + 1, day=1)

#     return dias_laborados_por_mes



# Revisado ✅
# @login_required
# def generar_detalles_contrato(request, contrato):
#     """
#     Genera registros de detalles del contrato con días laborados y valores a pagar por mes:
#     - Primer mes: días laborados y valor proporcional
#     - Meses intermedios: 30 días y valor completo del valor mensual a pagar
#     - Último mes: días laborados y valor proporcional
#     """

#     fecha_inicio = contrato.fecha_inicio
#     fecha_fin = contrato.fecha_fin
#     valor_mensual = contrato.valor_mensual_contrato

#     if not fecha_inicio or not fecha_fin or valor_mensual is None:
#         raise ValueError("El contrato debe tener fecha de inicio, fecha de fin y un valor mensual válido.")

#     valor_mensual = Decimal(valor_mensual)
#     # DetalleContratro.objects.filter(fk_contrato=contrato).delete()

#     # Calcular días laborados por mes
#     dias_laborados_por_mes = calcular_dias_laborados_por_mes(fecha_inicio, fecha_fin)
#     meses_ordenados = sorted(dias_laborados_por_mes.keys())
#     valor_dia = valor_mensual / 30

#     detalles = []

#     for idx, mes in enumerate(meses_ordenados):
#         dias = dias_laborados_por_mes[mes]
#         # Primer mes
#         if idx == 0:
#             if dias == 30:
#                 valor_mes = valor_mensual
#             else:
#                 valor_mes = round(dias * valor_dia, 2)
#         # Último mes
#         elif idx == len(meses_ordenados) - 1:
#             if dias == 30:
#                 valor_mes = valor_mensual
#             else:
#                 valor_mes = round(dias * valor_dia, 2)
#         # Meses intermedios
#         else:
#             dias = 30
#             valor_mes = valor_mensual

#         detalles.append(
#             DetalleContratro(
#                 fk_contrato=contrato,
#                 mes_a_pagar=mes,
#                 dias_laborados=dias,
#                 valor_a_pagar=valor_mes,
#             )
#         )

#     DetalleContratro.objects.bulk_create(detalles)
#     return detalles


# Revisado ✅
# @login_required
# def definir_contrato_usuario(request, usuario_id):
#     """
#     Muestra el formulario para definir el contrato de un empleado.
#     """
#     if request.method == "POST":
#         usuario = get_object_or_404(Empleado, id=usuario_id)
#         data = request.POST
#         try:
#             # Instanciar valores recibidos
#             fk_usuario = Empleado.objects.get(id=usuario.id)
#             if fk_periodo := data.get("fk_periodo"):
#                     fk_periodo = Periodo.objects.get(id=fk_periodo)
#             tipo_contrato = data.get("tipo_contrato")
#             if fk_dedicacion := data.get("fk_dedicacion"):
#                 fk_dedicacion = Dedicacion.objects.get(id=fk_dedicacion)
#             inicio_contrato = data.get("fecha_inicio_contrato")
#             fin_contrato = data.get("fecha_fin_contrato")
#             estado_contrato = data.get("estado_contrato")
#             fk_tipo_contrato = TipoContrato.objects.get(id=tipo_contrato)
#             if valor_mensual_contrato := data.get("valor_mensual_contrato"):
#                 valor_mensual_contrato = Decimal(valor_mensual_contrato.replace(",", ""))
#             total_dias_laborados_por_contrato = calcular_dias_laborados_por_contrato(inicio_contrato, fin_contrato)

#             # Convertir fechas a datetime
#             fecha_inicio_contrato = datetime.strptime(inicio_contrato, "%Y-%m-%d")
#             fecha_fin_contrato = datetime.strptime(fin_contrato, "%Y-%m-%d")

#             # Lógica segun el tipo de contrato
#             if estado_contrato == "1":
#                 # Agregar nuevo contrato
#                 contrato = Contrato.objects.create(
#                     fk_periodo=fk_periodo,
#                     fk_usuario=fk_usuario,
#                     fecha_inicio=fecha_inicio_contrato,
#                     fecha_fin=fecha_fin_contrato,
#                     fk_tipo_contrato=fk_tipo_contrato,
#                     fk_dedicacion=fk_dedicacion,
#                     vigencia_contrato=True,
#                     valor_mensual_contrato=valor_mensual_contrato,
#                     total_dias_laborados=total_dias_laborados_por_contrato
#                 )

#                 if valor_mensual_contrato is not None:
#                     generar_detalles_contrato(request, contrato)

#             if estado_contrato == "2":
#                 # Editar contrato existente
#                 print(data)
#                 pass

#             if estado_contrato == "3":
#                 # Anexar contrato
#                 print(data)
#                 pass

#             return JsonResponse({
#                 "status": "success",
#                 "message": "Contrato asignado correctamente."
#             })
#         except Exception as e:
#             print(traceback.format_exc())
#             return JsonResponse({
#                 "status": "error",
#                 "message": 'Error inesperado. Por favor, intente nuevamente.'
#             }, status=500)


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
            if fk_estado_revision := request.POST.get('fk_estado_revision'):
                usuario.fk_estado_revision = EstadoRevision.objects.get(id=fk_estado_revision)

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

def gestion_contratos_docentes(request):
    """
    Muestra la gestión de contratos
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    contexto.update ({
        'programa_list': Programa.objects.all(),
    })

    return render(request, 'docentes.html', contexto)


def gestion_contratos_administrativos(request):
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


def calcular_valor_a_pagar(total_horas, id_docente):
    """
    Calcula el valor a pagar según las horas semanales y el total de horas, además de la dedicación del docente.
    """
    fk_ultimo_nivel_estudio = Empleado.objects.get(id=id_docente).fk_ultimo_nivel_estudio
    tarifa_base = NivelAcademicoHistorico.objects.filter(fk_nivel_academico=fk_ultimo_nivel_estudio).order_by('-año_vigencia').first()
    if not tarifa_base:
        raise Exception("No existe tarifa base para el nivel académico del docente.")
    valor_a_pagar = total_horas * tarifa_base.tarifa_base_por_hora
    return valor_a_pagar

@login_required
def agregar_matriz_academica(request):
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
# ---------------------------- VISTA REPORTES ---------------------------------
#


@login_required
def reportes(request):
    contexto = obtener_db_info(request)

    return render(request, 'reportes.html', contexto)