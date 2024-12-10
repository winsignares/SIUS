from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from home.models.talento_humano.usuarios import Usuario
from django.db import IntegrityError

# Create your views here.

def login(request):
    return render(request, 'login.html')

def autenticar_usuario(request):
    if request.method == 'GET':
        login
    else:
        print(request.POST)
        # user = authenticate(
        #     request, username = request.POST['email'], password = request.POST['password'])
        # if user is None:
        #     return render(request, login, {"error": "Credenciales incorrectos. Intentelo nuevamente."})

        # auth_login(request, user)
        # return redirect('dashboard')
        login
        

def dashboard(request):
    return render(request, 'dashboard.html')

def actualizar_contraseña(request):
    if request.method == 'GET':
        login
    else:
        pass
