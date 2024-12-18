from django.template.loader import render_to_string
from django.db import models, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.core.paginator import Paginator
from .models.talento_humano.usuarios import Usuario
from .models.talento_humano.detalles_academicos import DetalleAcademico
from .models.talento_humano.detalles_exp_laboral import DetalleExperienciaLaboral
from .models.talento_humano.tipo_documentos import TipoDocumento
from .models.talento_humano.niveles_academicos import NivelAcademico
from .models.talento_humano.datos_adicionales import EPS, AFP, ARL, Departamento, CajaCompensacion, Institucion
from .models.talento_humano.roles import Rol


import openpyxl
from siuc import settings

# Create your views here.


def iniciar_sesion_form(request):
    '''
        Función para mostrar el formulario de inicio de sesión.
    '''

    return render(request, 'login.html')


def restablecer_contraseña_form(request):
    '''
        Función para mostrar el formulario de restablecer contraseña.
    '''

    return render(request, 'restablecer_contraseña.html')


def error_404_view(request, exception):
    """
    Vista para manejar errores 404.
    """
    return render(request, '404.html', status=404)


def signin(request):
    '''
        Función para manejar los datos enviados en el formulario de inicio de sesión.
    '''
    if request.method == 'GET':
        return redirect('iniciar_sesion_form')
    elif request.method == 'POST':
        print(request.POST)

        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verificar si el usuario existe en la base de datos
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            messages.error(
                request, "El correo ingresado no tiene una cuenta asociada.")
            return redirect('iniciar_sesion_form')

        user = authenticate(
            request,
            username=request.POST['email'],
            password=request.POST['password']
        )

        if user is None:
            messages.error(
                request, "La contraseña ingresada es incorrecta.")
            return render(request, 'login.html', {'email': email})

        login(request, user)

        return redirect('dashboard')


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
                request, "El correo ingresado no tiene una cuenta asociada.")
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

    # Contexto inicial
    contexto = {
        'usuario_log': usuario_log,
        'user_groups': grupos_usuario,
    }

    # Incluir datos adicionales si es necesario para otras funciones
    if incluir_datos_adicionales:
        contexto.update({
            'tipos_documento_list': TipoDocumento.objects.all(),
            'departamento_list': Departamento.objects.all(),
            'eps_list': EPS.objects.all(),
            'arl_list': ARL.objects.all(),
            'caja_compensacion_list': CajaCompensacion.objects.all(),
            'afp_list': AFP.objects.all(),
            'niveles_academicos_list': NivelAcademico.objects.all(),
            'rol_list': Rol.objects.all(),
            'instituciones_list': Institucion.objects.all().order_by('codigo'),
        })

    return contexto


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
# ----------------------------  GESTIÓN ASPIRANTES ---------------------------------
#


@login_required
def gestion_aspirantes(request):
    '''
        Función que maneja la vista de Aspirantes.
    '''
    # Obtener contexto con datos adicionales
    contexto = obtener_db_info(request, incluir_datos_adicionales=True)

    all_usuarios = Usuario.objects.all()

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

    # Paginación para la tabla de aspirantes en estado 'Pendiente'
    paginator_pendientes = Paginator(
        usuarios_aspirantes, 8)  # 5 registros por página
    page_number_pendientes = request.GET.get('page_pendientes')
    page_obj_pendientes = paginator_pendientes.get_page(page_number_pendientes)

    # Paginación para la tabla de aspirantes en estado 'Pendiente'
    paginator_rechazados = Paginator(
        usuarios_rechazados, 8)  # 8 registros por página
    page_number_rechazados = request.GET.get('page_rechazados')
    page_obj_rechazados = paginator_rechazados.get_page(page_number_rechazados)

    # Actualizar el contexto
    contexto.update({
        'page_obj_pendientes': page_obj_pendientes,
        'page_obj_rechazados': page_obj_rechazados,
        'aspirante_pendiente': aspirante_pendiente,
        'aspirante_rechazado': aspirante_rechazado,
    })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX request
        return render(request, 'partials/aspirantes_content.html', contexto)

    return render(request, 'aspirantes.html', contexto)


@login_required
def agregar_info_personal(request):
    print(request.POST)
    if request.method == 'POST':
        # Extraer todos los datos del formulario
        data = request.POST
        try:
            # Verificar si ya existe un usuario con el número de documento
            if Usuario.objects.filter(numero_documento=data.get('numero_documento')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ya existe un aspirante con el número de cédula ingresado.'
                }, status=400)

            # Crear un nuevo usuario
            nuevo_usuario = Usuario.objects.create(
                # Campos obligatorios
                fk_rol_id=data.get('fk_rol'),

                fk_tipo_documento_id=data.get('fk_tipo_documento'),

                cargo=data.get('cargo'),

                primer_nombre=data.get('primer_nombre'),

                primer_apellido=data.get('primer_apellido'),

                numero_documento=data.get('numero_documento'),

                correo_personal=data.get('correo_personal'),

                # Campos opcionales
                segundo_nombre=data.get('segundo_nombre') or None,
                segundo_apellido=data.get('segundo_apellido') or None,
                fecha_nacimiento=data.get('fecha_nacimiento') or None,
                lugar_nacimiento=data.get('lugar_nacimiento') or None,
                fecha_expedicion_documento=data.get('fecha_expedicion_documento') or None,
                lugar_expedicion_documento=data.get('lugar_expedicion_documento') or None,
                sexo=data.get('sexo') or None,
                celular=data.get('celular') or None,
                telefono_fijo=data.get('telefono_fijo') or None,
                direccion_residencia=data.get('direccion_residencia') or None,
                departamento_residencia=data.get('departamento_residencia') or None,
                ciudad_residencia=data.get('ciudad_residencia') or None,
                barrio_residencia=data.get('barrio_residencia') or None,
                estado_civil=data.get('estado_civil') or None,
                ultimo_nivel_estudio=data.get('ultimo_nivel_estudio') or None,
                eps=data.get('eps') or None,
                afp=data.get('afp') or None,
                url_hoja_de_vida=data.get('url_hoja_de_vida') or None,
                estado_revision="Pendiente",
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
                'message': 'Error de integridad al agregar el usuario. Revise los datos ingresados.'
            }, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'error',
                'message': f"Error inesperado: {e}"
            }, status=500)


def agregar_exp_laboral(request):
    print(request.POST)
    pass


def agregar_detalle_academico(request):
    print(request.POST)
    pass


@login_required
def gestion_empleados(request):
    '''
        Función que maneja la vista de Empleados
    '''

    contexto = obtener_db_info(request)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX request
        return render(request, 'partials/empleados_content.html', contexto)

    return render(request, 'empleados.html', contexto)


@login_required
def reportes(request):
    contexto = obtener_db_info(request)

    fecha_creacion = request.GET.get('fecha_creacion')
    estado = request.GET.get('estado')
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
    if estado:
        usuarios = usuarios.filter(estado_revision=estado)

    # Paginación: 5 registros por página
    paginator = Paginator(usuarios, 10)
    page_obj = paginator.get_page(page)

    # Actualizar el contexto con la paginación y filtros
    contexto.update({
        'page_obj': page_obj,
        # Mantener el filtro
        'fecha_creacion': request.GET.get('fecha_creacion', ''),
        'estado': request.GET.get('estado', '')  # Mantener el filtro
    })

    return render(request, 'reportes.html', contexto)



@login_required
def generar_reporte_excel(request):
    # Capturar filtros de la URL
    fecha_creacion = request.GET.get('fecha_creacion')
    estado = request.GET.get('estado')

    # Filtrar datos según los parámetros enviados
    usuarios = Usuario.objects.all()
    if fecha_creacion:
        usuarios = usuarios.filter(fecha_creacion__date=fecha_creacion)
    if estado:
        usuarios = usuarios.filter(estado_revision=estado)

    # Crear libro de Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Reporte SNIES"

    # Encabezados
    encabezados = ["ID", "Nombre Completo", "Cargo", "Número Documento", "Correo", "Estado", "Fecha Creación"]
    sheet.append(encabezados)

    # Insertar datos filtrados
    for idx, usuario in enumerate(usuarios, start=1):
        sheet.append([
            idx,  # ID autoincremental
            f"{usuario.primer_nombre} {usuario.primer_apellido}",
            usuario.cargo,
            usuario.numero_documento,
            usuario.correo_personal,
            usuario.estado_revision,
            usuario.fecha_creacion.strftime("%Y-%m-%d"),
        ])

    # Generar nombre de archivo personalizado
    nombre_archivo = "reporte_snies.xlsx"
    if estado:
        nombre_archivo = f"reporte_snies_{estado.lower()}.xlsx"

    # Respuesta HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    workbook.save(response)
    return response
