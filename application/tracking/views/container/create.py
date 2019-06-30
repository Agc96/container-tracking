from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from ...models import Carrier, Container, MockUser
from ...utils import RestResponse

import os

# Clave para acceso a Google Maps

def create(request):
    """Formulario de creación de un contenedor marítimo."""
    return render(request, 'tracking/container/create.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all(),
        'maps': os.getenv('TRACKING_MAPS_KEY', '')
    })

def save(request):
    # TODO: Implementar lógica de guardado de contenedor
    valid, message = Container.validate_and_create(request.POST)
    if not valid:
        return RestResponse(True, message)
    # reverse('container-index')
    return JsonResponse({
        'error': False,
        'message': 'Contenedor guardado correctamente.',
        'url': reverse('container-index')
    })

def validate_container(request):
    pass
