from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ...models import Carrier, Container, MockUser

import os

# Clave para acceso a Google Maps

def create(request):
    """Formulario de creación de un contenedor marítimo."""
    return render(request, 'tracking/container/create.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all(),
        'maps': os.getenv('GOOGLE_MAPS_KEY', '')
    })

def save(request):
    # TODO: Implementar lógica de guardado de contenedor
    code = request.GET.get('code')
    if not Container.validate_code(code):
        return HttpResponse('El código del contenedor debe tener un formato de 4 letras más 7 dígitos.')
    return HttpResponseRedirect(reverse('container-index'), {
        'user': MockUser(),
        'carriers': Carrier.objects.all(),
        'message': 'Contenedor guardado correctamente.'
    })

def validate_container(request):
    pass
