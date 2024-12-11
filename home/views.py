from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from home.models.talento_humano.usuarios import Usuario
from django.db import IntegrityError

# Create your views here.
def welcome(request):
    return render(request, 'login.html')

def iniciar_sesion(request):
    if request.method == 'GET':
        return redirect('welcome')
    elif request.method == 'POST':
        print(request.POST)
    
        user = authenticate(
            request,
            username = request.POST['email'],
            password = request.POST['password']
        )            
        if user is None:
            messages.error(request, "Credenciales incorrectos. Intentelo nuevamente.")
            return redirect('welcome')
        
        login(request, user)
        return redirect('dashboard')

def actualizar_contraseña(request):
    if request.method == 'GET':
        return redirect('welcome')
    else:
        print(request.POST)
        
        return redirect('welcome')

def dashboard(request):
    return render(request, 'dashboard.html')

def cerrar_sesion(request):
    logout(request)
    return redirect ('iniciar_sesion')

