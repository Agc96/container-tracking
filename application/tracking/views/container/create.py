from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ...models import Carrier, MockUser

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
    return HttpResponseRedirect(reverse('container-index'))
