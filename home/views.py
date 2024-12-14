from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models.talento_humano.usuarios import Usuario
from .models.talento_humano.tipo_documentos import TipoDocumento
from .models.talento_humano.niveles_academicos import NivelAcademico
from .models.talento_humano.datos_adicionales import EPS, AFP, ARL, Departamento, CajaCompensacion
from .models.talento_humano.roles import Rol
from siuc import settings

# Create your views here.


def iniciar_sesion_form(request):
    # Capturar el mensaje de alerta si la sesión expiró
    if request.GET.get('alert') == 'session_expired':
        messages.warning(
            request, "Se ha cerrado la sesión por inactividad por más de 30 minutos.")

    return render(request, 'login.html')


def restablecer_contraseña_form(request):

    return render(request, 'restablecer_contraseña.html')


def tiempo_expirado(request):
    if not request.user.is_authenticated:
        logout(request)
        return redirect(f"{settings.LOGIN_URL}?alert=session_expired&next={request.path}")


def signin(request):
    if request.method == 'GET':
        return redirect('iniciar_sesion_form')
    elif request.method == 'POST':
        print(request.POST)

        user = authenticate(
            request,
            username=request.POST['email'],
            password=request.POST['password']
        )
        if user is None:
            messages.error(
                request, "Credenciales incorrectos. Intentelo nuevamente.")
            return redirect('iniciar_sesion_form')

        login(request, user)

        return redirect('dashboard')


def actualizar_contraseña(request):
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
            return redirect('restablecer_contraseña_form')

        # Actualizar la contraseña
        user.set_password(new_password)
        user.save()

        # Enviar mensaje de éxito
        messages.success(
            request, "Contraseña actualizada exitosamente. Ingrese con sus nuevas credenciales.")

        return redirect('iniciar_sesion_form')


def obtener_contexto(request):
    """
    Función auxiliar para obtener el contexto del usuario autenticado.
    """
    usuario_autenticado = request.user
    grupos_usuario = usuario_autenticado.groups.values_list('name', flat=True)

    try:
        usuario = Usuario.objects.get(auth_user=usuario_autenticado)
        usuario.primer_nombre = usuario.primer_nombre.capitalize()
        usuario.primer_apellido = usuario.primer_apellido.capitalize()
        usuario.cargo = usuario.cargo.upper()
    except Usuario.DoesNotExist:
        usuario = None

    return {
        'usuario': usuario,
        'user_groups': grupos_usuario,
    }


@login_required
def dashboard(request):

    tiempo_expirado(request)

    contexto = obtener_contexto(request)

    return render(request, 'inicio.html', contexto)


@login_required
def cerrar_sesion(request):
    logout(request)

    return redirect('iniciar_sesion_form')


@login_required
def gestion_aspirantes(request):

    tiempo_expirado(request)

    contexto = obtener_contexto(request)
    tipos_documento = TipoDocumento.objects.all()
    niveles_academicos = NivelAcademico.objects.all()
    departamento_list = Departamento.objects.all()
    eps_list = EPS.objects.all()
    arl_list = ARL.objects.all()
    caja_compensacion_list = CajaCompensacion.objects.all()
    afp_list = AFP.objects.all()
    rol_list = Rol.objects.all()

    # Agregar variable al contexto
    contexto.update({
        'tipos_documento': tipos_documento,
        'departamento_list': departamento_list,
        'eps_list': eps_list,
        'arl_list': arl_list,
        'caja_compensacion_list': caja_compensacion_list,
        'afp_list': afp_list,
        'niveles_academicos': niveles_academicos,
        'rol_list': rol_list
    })

    return render(request, 'aspirantes.html', contexto)


@login_required
def gestion_empleados(request):

    tiempo_expirado(request)

    contexto = obtener_contexto(request)

    return render(request, 'empleados.html', contexto)


@login_required
def reportes(request):

    tiempo_expirado(request)

    contexto = obtener_contexto(request)

    return render(request, 'reportes.html', contexto)
