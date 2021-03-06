import json
import os

from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.shortcuts import redirect, render

from ...models import Container, Movement, MovementStatus
from ...utils import DATETIME_FORMAT
from .utils import format_date

SCHARFF = 4
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
    # Formatear fecha de llegada estimada, si es que existe
    container.formatted_arrival_date = format_date(container.arrival_date, 'No especificada')
    # Obtener lista de movimientos
    movements = Movement.objects.filter(container=container)
    locations = []
    for movement in movements:
        # Formatear estado del movimiento
        try:
            # TODO: ID de la empresa debe guardarse en un registro 1 a 1 con el usuario de Django
            movement.translation = MovementStatus.objects.get(status=movement.status.status, enterprise_id=SCHARFF)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            movement.translation = movement.status
        # Formatear fecha del movimiento
        movement.formatted_date = format_date(movement.date, 'Desconocida')
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
        'maps': os.getenv('MAPS_KEY', '')
    })
