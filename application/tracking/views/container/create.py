from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from ...models import Enterprise, Container
from ...utils import RestResponse

import os

def create(request):
    """Formulario de creación de un contenedor marítimo."""
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'tracking/container/create.html', {
        'fullname': request.user.first_name + ' ' + request.user.last_name,
        'carriers': Enterprise.objects.filter(carrier=True),
        'maps': os.getenv('MAPS_KEY', '')
    })

def save(request):
    if not request.user.is_authenticated:
        return RestResponse(True, 'Debe iniciar sesión para continuar.')
    # Validar que los 
    valid, message = Container.validate_and_create(request.POST)
    if not valid:
        return RestResponse(True, message)
    # Enviar mensaje para mostrarse en la siguiente pantalla
    messages.success(request, 'Contenedor guardado correctamente.')
    return RestResponse(False, None)
