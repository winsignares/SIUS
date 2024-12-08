from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from home.models.talento_humano.usuarios import Usuario

# Create your views here.

def login(request):
    return render(request, 'login.html')

def autenticar_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Autenticación del usuario
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            # Verificar si el usuario está relacionado con un perfil en "usuarios"
            try:
                usuario = Usuario.objects.get(auth_user=user)
                # Redirigir al dashboard
                print("Inicio de sesión exitoso.")
                return redirect('/dashboard/')
            except Usuario.DoesNotExist:
                messages.error(request, "El usuario no está vinculado a un perfil válido.")
                print("Inicio de sesión denegado.")
                return redirect('/login/')
        else:
            # Mostrar mensaje de error si las credenciales no son válidas
            messages.error(request, "Credenciales inválidas. Intente de nuevo.")
            return redirect('/login/')

    # Renderizar el formulario de inicio de sesión si es un GET
    return render(request, 'login.html')