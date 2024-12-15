from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin


class CustomLoginRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Verificar si el usuario no está autenticado pero está accediendo a una página protegida
        if not request.user.is_authenticated and request.path.startswith('/siuc/dashboard/'):
            # Añadir mensaje de sesión expirada
            messages.warning(
                request, "Sesión cerrada por inactividad. Ingrese nuevamente.")
            # Redirigir al login
            return redirect(f"/siuc/login/?next={request.path}")
