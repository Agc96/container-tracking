from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

def index(request):
    """Formulario de inicio de sesión."""
    return render(request, 'tracking/login.html', {
        'user': None
    })

def login(request):
    """Validación de datos y lógica de inicio de sesión."""
    # TODO: Implementar lógica de inicio de sesión
    return HttpResponseRedirect(reverse('container-index'))

def profile(request):
    """Configuración del perfil de un usuario."""
    return HttpResponse('TODO: Perfil')

def logout(request):
    # TODO: Implementar lógica de cierre de sesión
    return HttpResponseRedirect(reverse('index'))
