from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime, timedelta
from django.contrib.auth import logout


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            now = datetime.now()
            last_activity = request.session.get('last_activity')

            if last_activity:
                last_activity_time = datetime.fromisoformat(last_activity)

                # Verificar si ha pasado el tiempo máximo permitido
                if (now - last_activity_time).total_seconds() > settings.SESSION_COOKIE_AGE:
                    # Cerrar la sesión
                    logout(request)
                    # Redirige al login con un mensaje de alerta
                    return redirect(f"{settings.LOGIN_URL}?alert=session_expired&next={request.path}")

            # Actualizar la última actividad
            request.session['last_activity'] = now.isoformat()

        response = self.get_response(request)
        return response
