from collections import defaultdict
import json
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
from .models.talento_humano.usuarios import Usuario
from .models.talento_humano.detalles_academicos import DetalleAcademico
from .models.talento_humano.detalles_exp_laboral import DetalleExperienciaLaboral
from .models.talento_humano.tipo_documentos import TipoDocumento
from .models.talento_humano.niveles_academicos import NivelAcademico
from .models.talento_humano.datos_adicionales import EPS, AFP, ARL, Departamento, CajaCompensacion, Institucion, Sede
from .models.talento_humano.roles import Rol
from .models.talento_humano.contrato import Contrato
from .models.carga_academica import CargaAcademica, Materia, Periodo, Programa, Semestre
from siuc import settings
import openpyxl
import pytz
import pandas

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
        usuario_log = Usuario.objects.get(auth_user=usuario_autenticado)
        usuario_log.primer_nombre = usuario_log.primer_nombre.capitalize()
        usuario_log.primer_apellido = usuario_log.primer_apellido.capitalize()
        usuario_log.cargo = usuario_log.cargo.upper()
    except Usuario.DoesNotExist:
        usuario_log = None

    # Obtener el programa del usuario logueado (Almacenado en first_name)
    programa_usuario = Programa.objects.filter(programa=usuario_autenticado.first_name).first()

    # Obtener el número de semestres del programa
    num_semestres = int(programa_usuario.numero_semestres) if programa_usuario else 0

    # Filtrar los semestres hasta el número del programa
    semestres_list = Semestre.objects.filter(id__lte=num_semestres).order_by("id")

    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    # Contexto inicial
    contexto = {
        'usuario_log': usuario_log,
        'user_groups': grupos_usuario,
        'semestres_list': semestres_list,
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
            'materias_list': Materia.objects.all(),
            'periodos_list': Periodo.objects.all(),
            'docentes_list': Usuario.objects.filter(fk_rol_id=4),
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
        print(request.POST)

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
        print(request.POST)

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
    usuarios_aspirantes = Usuario.objects.filter(
        estado_revision='Pendiente').order_by('-fecha_modificacion')
    # Término de búsqueda para aspirantes en estado 'Rechazado'
    aspirante_rechazado = request.GET.get('aspirante_rechazado', '').strip()
    usuarios_rechazados = Usuario.objects.filter(
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


@login_required
def agregar_aspirante(request):
    print(request.POST)
    if request.method == 'POST':
        data = request.POST
        try:
            if Usuario.objects.filter(numero_documento=data.get('numero_documento')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un aspirante con el número de documento ingresado.'}, status=400)

            if Usuario.objects.filter(correo_personal=data.get('correo_personal')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un aspirante con el correo personal ingresado.'}, status=400)

            nuevo_usuario = Usuario.objects.create(
                fk_rol_id=data.get('fk_rol'),
                fk_tipo_documento_id=data.get('fk_tipo_documento'),
                cargo=data.get('cargo'),
                primer_nombre=data.get('primer_nombre'),
                primer_apellido=data.get('primer_apellido'),
                numero_documento=data.get('numero_documento'),
                correo_personal=data.get('correo_personal'),
                segundo_nombre=data.get('segundo_nombre'),
                segundo_apellido=data.get('segundo_apellido'),
                fecha_nacimiento=data.get('fecha_nacimiento'),
                lugar_nacimiento=data.get('lugar_nacimiento'),
                fecha_expedicion_documento=data.get('fecha_expedicion_documento'),
                lugar_expedicion_documento=data.get('lugar_expedicion_documento'),
                sexo=data.get('sexo'),
                celular=data.get('celular'),
                telefono_fijo=data.get('telefono_fijo'),
                direccion_residencia=data.get('direccion_residencia'),
                departamento_residencia=data.get('departamento_residencia'),
                ciudad_residencia=data.get('ciudad_residencia'),
                barrio_residencia=data.get('barrio_residencia'),
                estado_civil=data.get('estado_civil'),
                ultimo_nivel_estudio=data.get('ultimo_nivel_estudio'),
                fk_eps_id=data.get('fk_eps'),
                afp=data.get('afp'),
                url_hoja_de_vida=data.get('url_hoja_de_vida'),
                estado_revision="Pendiente",
                sede_donde_labora=data.get('sede_donde_labora'),
                fk_creado_por=request.user
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Aspirante agregado correctamente.',
                'usuario_id': nuevo_usuario.id
            })

        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad al agregar el aspirante. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': f"Error inesperado: {e}"
            }, status=500)

@login_required
def agregar_empleado(request):
    if request.method == 'POST':
        data = request.POST
        try:
            # Verificar si ya existe un usuario con el número de documento ingresado
            if Usuario.objects.filter(numero_documento=data.get('numero_documento')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un empleado con el número de documento ingresado.'}, status=400)

            # Verificar si ya existe un usuario con el correo
            if Usuario.objects.filter(correo_personal=data.get('correo_personal')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un empleado con el correo personal ingresado.'}, status=400)

            # Crear un nuevo usuario
            nuevo_usuario = Usuario.objects.create(
                fk_rol_id=data.get('fk_rol_emp'),
                fk_tipo_documento_id=data.get('fk_tipo_documento'),
                cargo=data.get('cargo'),
                primer_nombre=data.get('primer_nombre'),
                primer_apellido=data.get('primer_apellido'),
                numero_documento=data.get('numero_documento'),
                correo_personal=data.get('correo_personal'),
                segundo_nombre=data.get('segundo_nombre'),
                segundo_apellido=data.get('segundo_apellido'),
                fecha_nacimiento=data.get('fecha_nacimiento'),
                lugar_nacimiento=data.get('lugar_nacimiento'),
                fecha_expedicion_documento=data.get('fecha_expedicion_documento'),
                lugar_expedicion_documento=data.get('lugar_expedicion_documento'),
                sexo=data.get('sexo'),
                celular=data.get('celular'),
                telefono_fijo=data.get('telefono_fijo'),
                direccion_residencia=data.get('direccion_residencia'),
                departamento_residencia=data.get('departamento_residencia'),
                ciudad_residencia=data.get('ciudad_residencia'),
                barrio_residencia=data.get('barrio_residencia'),
                estado_civil=data.get('estado_civil'),
                ultimo_nivel_estudio=data.get('ultimo_nivel_estudio'),
                fk_eps_id=data.get('fk_eps'),
                afp=data.get('afp'),
                url_hoja_de_vida=data.get('url_hoja_de_vida'),
                estado_revision="Contratado",
                activo=True,
                sede_donde_labora=data.get('sede_donde_labora'),
                fk_creado_por=request.user
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Empleado agregado correctamente.',
                'usuario_id': nuevo_usuario.id
            })

        except IntegrityError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error de integridad al agregar el empleado: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Error inesperado: {str(e)}"
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
        titulo_obtenido = request.POST.get("titulo_obtenido")
        nivel_academico_id = request.POST.get("nivel_academico")
        fecha_graduacion = request.POST.get("fecha_graduacion")

        try:
            # Validar que el usuario existe
            usuario = get_object_or_404(Usuario, id=usuario_id)

            # Crear el detalle académico
            detalle = DetalleAcademico.objects.create(
                usuario=usuario,
                institucion=institucion,
                titulo_obtenido=titulo_obtenido,
                nivel_academico_id=nivel_academico_id,
                fecha_graduacion=fecha_graduacion
            )

            contexto = {
                "detalle": {
                    "institucion": detalle.institucion,
                    "titulo_obtenido": detalle.titulo_obtenido,
                    "nivel_academico": detalle.nivel_academico.nombre,
                    "fecha_graduacion": detalle.fecha_graduacion,
                }
            }

            return JsonResponse({"status": "success", "message": "Detalle académico agregado exitosamente.", "detalle": contexto["detalle"]})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error al agregar el detalle académico: {e}"})

    return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)


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

        try:
            # Validar que el usuario existe
            usuario = get_object_or_404(Usuario, id=usuario_id)

            # Crear el detalle de experiencia laboral
            detalle = DetalleExperienciaLaboral.objects.create(
                usuario=usuario,
                empresa=empresa,
                cargo=cargo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            contexto = {
                "detalle": {
                    "empresa": detalle.empresa,
                    "cargo": detalle.cargo,
                    "fecha_inicio": detalle.fecha_inicio,
                    "fecha_fin": detalle.fecha_fin,
                }
            }

            return JsonResponse({"status": "success", "message": "Experiencia laboral agregada exitosamente.", "detalle": contexto["detalle"]})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error al agregar la experiencia laboral: {e}"})

    return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)


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
    empleados_activos = Usuario.objects.filter(activo=True, estado_revision='Contratado').order_by('-fecha_modificacion')
    # Término de búsqueda para aspirantes en estado 'Rechazado'
    empleado_inactivo = request.GET.get('empleado_inactivo', '').strip()
    empleados_inactivos = Usuario.objects.filter(activo=False, estado_revision='Contratado').order_by('-fecha_modificacion')

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
@csrf_exempt
def cargar_empleados_masivamente(request):
    if request.method == 'POST' and 'archivoExcel' in request.FILES:
        archivo = request.FILES['archivoExcel']
        try:
            # Leer el archivo Excel usando pandas
            import pandas as pd
            datos = pd.read_excel(archivo)

            # Validar que las columnas requeridas existan en el archivo
            columnas_requeridas = [
                'primer_nombre', 'primer_apellido', 'fk_rol', 'cargo',
                'fecha_nacimiento', 'fk_tipo_documento', 'numero_documento',
                'correo_personal', 'celular', 'departamento_residencia',
                'ultimo_nivel_estudio', 'eps', 'afp'
            ]
            if not all(col in datos.columns for col in columnas_requeridas):
                return JsonResponse({
                    'status': 'error',
                    'message': f"El archivo debe contener las columnas: {', '.join(columnas_requeridas)}"
                }, status=400)

            # Validar que todos los roles en el Excel existen
            roles_no_encontrados = set(
                datos['fk_rol']) - set(Rol.objects.values_list('descripcion', flat=True))
            if roles_no_encontrados:
                return JsonResponse({
                    'status': 'error',
                    'message': f"Los siguientes roles no existen en la base de datos: {', '.join(roles_no_encontrados)}"
                }, status=400)

            # Iterar sobre las filas del archivo y crear empleados
            for _, fila in datos.iterrows():
                try:
                    # Validar que el rol existe
                    rol = Rol.objects.get(descripcion=fila['fk_rol'])
                    tipo_documento = TipoDocumento.objects.get(
                        descripcion=fila['fk_tipo_documento'])

                    # Crear o actualizar el usuario
                    Usuario.objects.update_or_create(
                        numero_documento=fila['numero_documento'],
                        defaults={
                            'primer_nombre': fila['primer_nombre'],
                            'primer_apellido': fila['primer_apellido'],
                            'fk_rol': rol,
                            'cargo': fila['cargo'],
                            'fecha_nacimiento': fila['fecha_nacimiento'],
                            'fk_tipo_documento': tipo_documento,
                            'correo_personal': fila['correo_personal'],
                            'celular': fila['celular'],
                            'departamento_residencia': fila['departamento_residencia'],
                            'ultimo_nivel_estudio': fila['ultimo_nivel_estudio'],
                            'eps': fila['eps'],
                            'afp': fila['afp'],
                            'estado_revision': 'Contratado',
                            'activo': True,
                            'fk_creado_por': request.user
                        }
                    )
                except Rol.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Error al procesar la fila con documento {fila['numero_documento']}: Rol '{fila['fk_rol']}' no encontrado. Verifica que el rol exista en la base de datos."
                    }, status=400)
                except TipoDocumento.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Error al procesar la fila con documento {fila['numero_documento']}: Tipo de Documento '{fila['fk_tipo_documento']}' no encontrado. Verifica que exista en la base de datos."
                    }, status=400)

            return JsonResponse({'status': 'success', 'message': 'Carga masiva realizada con éxito.'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Error al procesar el archivo: {e}"
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)


#
# ---------------------------- FUNCIONES PARA VISTAS ASPIRANTES Y EMPLEADOS ---------------------------------
#


@login_required
def detalle_usuario(request, tipo, usuario_id):
    """
    Muestra los detalles de un aspirante o empleado según el tipo y el estado del usuario.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
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
def editar_usuario(request, tipo, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    # Obtener el contrato más reciente del usuario (si existe)
    contrato = Contrato.objects.filter(fk_usuario=usuario).order_by('-fecha_inicio').first()

    contexto.update({
        "usuario": usuario,
        "tipo": tipo,
        "contrato": contrato  # Pasamos un solo contrato, no una queryset
    })

    return render(
        request,
        "partials/editar_usuario_form.html",
        contexto,
    )


def calcular_dias_laborados(fecha_inicio, fecha_fin):
    if fecha_inicio and fecha_fin:
        return (fecha_fin - fecha_inicio).days
    return 0


@login_required
def contrato_usuario(request, tipo, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    data = request.POST

    try:
        # Si el usuario es contratado, actualizar o crear el contrato
        contrato, created = Contrato.objects.get_or_create(
            fk_usuario=usuario,
            defaults={
                'fecha_inicio': data.get('fecha_inicio_contrato'),
                'fecha_fin': data.get('fecha_fin_contrato'),
                'valor_contrato': data.get('valor_contrato'),
                'tipo_contrato': data.get('tipo_contrato')
            }
        )
        if not created:
            contrato.fecha_inicio = data.get('fecha_inicio_contrato')
            contrato.fecha_fin = data.get('fecha_fin_contrato')
            contrato.valor_contrato = data.get('valor_contrato')
            contrato.tipo_contrato = data.get('tipo_contrato')
            contrato.save()
        else:
            # Si el estado no es "Contratado", desactivar el usuario y eliminar el contrato si existe
            usuario.activo = False
            Contrato.objects.filter(fk_usuario=usuario).delete()

        # Respuesta en formato JSON para manejo en el frontend
        return JsonResponse({
            'status': 'success',
            'message': 'Contrato creado/actualizado correctamente.'
        })
    except IntegrityError:
        return JsonResponse({
            'status': 'error',
            'message': 'Error de integridad al crear/actualizar el contrato.'
        }, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({
            'status': 'error',
            'message': f"Error inesperado: {e}"
        }, status=500)


@login_required
def actualizar_usuario(request, tipo, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == "POST":
        # Extraer todos los datos del formulario
        data = request.POST
        try:
            # Verificar si ya existe otro usuario con el mismo número de documento
            if Usuario.objects.filter(numero_documento=data.get('numero_documento')).exclude(id=usuario_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe otro usuario con el número de documento ingresado.'}, status=400)

            # Verificar si ya existe otro usuario con el mismo correo personal
            if Usuario.objects.filter(correo_personal=data.get('correo_personal')).exclude(id=usuario_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe otro usuario con el correo personal ingresado.'}, status=400)

            # Actualización de campos de Usuario
            usuario.primer_nombre = request.POST.get("primer_nombre", usuario.primer_nombre)
            usuario.segundo_nombre = request.POST.get("segundo_nombre", usuario.segundo_nombre)
            usuario.primer_apellido = request.POST.get("primer_apellido", usuario.primer_apellido)
            usuario.segundo_apellido = request.POST.get("segundo_apellido", usuario.segundo_apellido)
            usuario.numero_documento = request.POST.get("numero_documento", usuario.numero_documento)
            usuario.fecha_expedicion_documento = request.POST.get("fecha_expedicion_documento", usuario.fecha_expedicion_documento)
            usuario.lugar_expedicion_documento = request.POST.get("lugar_expedicion_documento", usuario.lugar_expedicion_documento)
            usuario.sexo = request.POST.get("sexo", usuario.sexo)
            usuario.celular = request.POST.get("celular", usuario.celular)
            usuario.telefono_fijo = request.POST.get("telefono_fijo", usuario.telefono_fijo)
            usuario.direccion_residencia = request.POST.get("direccion_residencia", usuario.direccion_residencia)
            usuario.departamento_residencia = request.POST.get("departamento_residencia", usuario.departamento_residencia)
            usuario.ciudad_residencia = request.POST.get("ciudad_residencia", usuario.ciudad_residencia)
            usuario.barrio_residencia = request.POST.get("barrio_residencia", usuario.barrio_residencia)
            usuario.estado_civil = request.POST.get("estado_civil", usuario.estado_civil)
            usuario.fecha_nacimiento = request.POST.get("fecha_nacimiento", usuario.fecha_nacimiento)
            usuario.lugar_nacimiento = request.POST.get("lugar_nacimiento", usuario.lugar_nacimiento)
            usuario.cargo = request.POST.get("cargo", usuario.cargo)
            usuario.ultimo_nivel_estudio = request.POST.get("ultimo_nivel_estudio", usuario.ultimo_nivel_estudio)
            usuario.estado_revision = request.POST.get("estado_revision", usuario.estado_revision)
            usuario.url_hoja_de_vida = request.POST.get("url_hoja_de_vida", usuario.url_hoja_de_vida)
            usuario.sede_donde_labora = request.POST.get("sede_donde_labora", usuario.sede_donde_labora)
            usuario.correo_personal = request.POST.get("correo_personal", usuario.correo_personal)
            usuario.fk_modificado_por = request.user

            rol_id = request.POST.get("fk_rol")
            tipo_documento_id = request.POST.get("fk_tipo_documento")
            eps_id = request.POST.get("fk_eps")

            if rol_id:
                usuario.fk_rol = Rol.objects.get(id=rol_id)
            if tipo_documento_id:
                usuario.fk_tipo_documento = TipoDocumento.objects.get(id=tipo_documento_id)
            if eps_id:
                usuario.fk_eps = EPS.objects.get(id=eps_id)

            # Si el usuario es contratado, llamar a la función contrato_usuario
            if usuario.estado_revision == 'Contratado':
                usuario.activo = True
                contrato_response = contrato_usuario(request, tipo, usuario_id)
                if contrato_response.status_code != 200:
                    return contrato_response
            # Guardar cambios
            usuario.save()

            # Respuesta en formato JSON para manejo en el frontend
            return JsonResponse({
                'status': 'success',
                'message': 'Usuario actualizado correctamente.'})
        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad al agregar el usuario. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': f"Error inesperado: {e}"
            }, status=500)


#
# ----------------------------  VISTA CARGA ACADEMICA ---------------------------------
#

def gestion_func_sustantivas(request):
    """
    Muestra la gestión de contratos
    """
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    dia_actual = datetime.now().date()

    contexto.update({
            "dia_actual": dia_actual,
        })

    return render(request, 'func_sustantivas.html', contexto)

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
@csrf_exempt
def guardar_matriz(request):
    """
    Guarda la carga académica del usuario.
    """
    if request.method == "POST":
        # Obtener datos del formulario
        data = json.loads(request.body)

        try:
            for carga in data[carga]:
                CargaAcademica.objects.create(
                )
            return JsonResponse({
                'status': 'success',
                'message': 'Carga académica agregada correctamente.'})
        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad al agregar la carga académica. Revise los datos ingresados.'
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
    usuarios = Usuario.objects.all()
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
    usuarios = Usuario.objects.all()
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
