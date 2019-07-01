from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from ...models import Container, Movement

import json
import os

DOUBLE_ROUND_DIGITS = 4

def detail(request, container_id):
    """Detalles de un contenedor marítimo."""
    if not request.user.is_authenticated:
        return redirect('index')
    # Obtener datos del contenedor
    try:
        container = Container.objects.get(pk=container_id)
    except ObjectDoesNotExist:
        messages.error(request, 'El contenedor no existe.')
        return redirect('container-index')
    # Obtener lista de movimientos
    movements = Movement.objects.filter(container=container)
    locations = []
    for movement in movements:
        # Formatear ubicación, latitud y longitud
        location = movement.location.name
        movement.formatted_location = location.replace('\n', '. ')
        latitude = movement.location.latitude
        movement.formatted_latitude = round(latitude, DOUBLE_ROUND_DIGITS) if latitude else 'Desconocida'
        longitude = movement.location.longitude
        movement.formatted_longitude = round(longitude, DOUBLE_ROUND_DIGITS) if longitude else 'Desconocida'
        # Agregar datos de geolocalización
        locations.append({
            'name': location.split('\n')[-1],
            'latitude': latitude,
            'longitude': longitude
        })
    # Renderizar la plantilla HTML
    return render(request, 'tracking/container/detail.html', {
        'fullname': request.user.first_name + ' ' + request.user.last_name,
        'container': container,
        'movements': movements,
        'locations': json.dumps(locations),
        'maps': os.getenv('TRACKING_MAPS_KEY', '')
    })
