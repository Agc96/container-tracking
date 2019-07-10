from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from ..utils import is_empty

def index(request):
    """Formulario de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('container-index')
    return render(request, 'tracking/login.html')

def login(request):
    """Validación de datos y lógica de inicio de sesión."""
    # Verificar que no se haya iniciado sesión
    if request.user.is_authenticated:
        return redirect('container-index')
    # Verificar que el usuario
    if request.method != 'POST':
        return redirect('index')
    # Verificar datos de entrada
    username = request.POST.get('username')
    if is_empty(username):
        return login_failed(request, 'Ingrese el nombre del usuario.')
    password = request.POST.get('password')
    if is_empty(password):
        return login_failed(request, 'Ingrese la contraseña')
    # Autenticar al usuario
    user = authenticate(request, username=username, password=password)
    if user is not None:
        django_login(request, user)
        return redirect('container-index')
    else:
        return login_failed(request, 'El nombre de usuario o la contraseña no son válidos.')

def login_failed(request, message):
    messages.error(request, message)
    return redirect('index')

def profile(request):
    """Configuración del perfil de un usuario."""
    if not request.user.is_authenticated:
        return redirect('index')
    return HttpResponse('TODO: Perfil')

def logout(request):
    django_logout(request)
    return redirect('index')
