from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Carrier

# TODO: Reemplazar esto con una llamada a getenv()
MAPS_KEY = 'KEY'

# Vistas del sistema de información: Inicio de sesión

def index(request):
    """Formulario de inicio de sesión."""
    return render(request, 'tracking/login.html', {
        'user': None
    })

def login(request):
    """Validación de datos y lógica de inicio de sesión."""
    # TODO: Implementar lógica de inicio de sesión
    return HttpResponseRedirect(reverse('container-list'))

# Vistas del sistema de información: Lista de contenedores

def container_list(request):
    """Búsqueda y listado de contenedores marítimos."""
    return render(request, 'tracking/container/list.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all()
    })

def container_import(request):
    # TODO: Implementar lógica para importar lista de contenedores
    return HttpResponse('TODO: Importar lista de contenedores')

def container_export(request):
    # TODO: Implementar lógica para exportar lista de contenedores
    return HttpResponse('TODO: Exportar lista de contenedores')

# Vistas del sistema de información: Detalles del contenedor

def container_detail(request, container_id):
    """Detalles de un contenedor marítimo."""
    return render(request, 'tracking/container/detail.html', {
        'user': MockUser(),
        'container_id': container_id,
        'carriers': Carrier.objects.all()
    })

# Vistas del sistema de información: Creación de contenedores

def container_create(request):
    """Formulario de creación de un contenedor marítimo."""
    return render(request, 'tracking/container/create.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all(),
        'maps_key': MAPS_KEY
    })

def container_save(request):
    # TODO: Implementar lógica de guardado de contenedor
    return HttpResponseRedirect(reverse('container-list'))

# Vistas del sistema de información: Opciones de usuario

def profile(request):
    """Configuración del perfil de un usuario."""
    return HttpResponse('TODO: Perfil')

def logout(request):
    # TODO: Implementar lógica de cierre de sesión
    return HttpResponseRedirect(reverse('index'))

# Funciones auxiliares

class MockUser():
    fullname = 'Anthony Gutiérrez'
    role = 'Administrador'
