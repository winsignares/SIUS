from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin


class CustomLoginRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        Middleware para gestionar la expiración de sesiones y redirigir a los usuarios no autenticados.
        """
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            self._handle_authenticated_user(request)
        else:
            self._handle_unauthenticated_user(request)

    def _handle_authenticated_user(self, request):
        """
        Lógica para usuarios autenticados:
        - Actualiza la última actividad.
        - Verifica el tiempo máximo permitido de inactividad.
        """
        now = datetime.now()
        last_activity = request.session.get('last_activity')

        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)

            # Verificar si ha pasado el tiempo máximo permitido
            if (now - last_activity_time).total_seconds() > settings.SESSION_COOKIE_AGE:
                self._logout_user(request)
                return

        # Si no ha excedido el tiempo de inactividad, actualizar la última actividad
        request.session['last_activity'] = now.isoformat()

    def _handle_unauthenticated_user(self, request):
        """
        Lógica para usuarios no autenticados:
        - Redirige al login si intentan acceder a vistas protegidas.
        """
        # Redirigir si acceden a rutas protegidas
        if request.path.startswith('/siuc/dashboard/'):
            messages.warning(
                request, "Sesión cerrada por inactividad. Ingrese nuevamente.")
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    def _logout_user(self, request):
        """
        Cierra la sesión del usuario y redirige con un mensaje.
        """
        logout(request)
        messages.warning(
            request, "Se ha cerrado la sesión por inactividad por más de 30 minutos.")
