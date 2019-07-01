from django.http import HttpResponse
from django.urls import reverse

from .utils import prepare_query
from ...models import Container
from ...utils import RestResponse

import csv

def import_data(request):
    """Crea varios contenedores a partir de un archivo CSV."""
    # Obtener archivo de contenedores
    file = request.FILES.get('file')
    if file is None:
        return RestResponse(True, 'No se ha subido ningún archivo.')
    # Validar que el archivo no sea muy grande
    if file.multiple_chunks():
        return RestResponse(True, 'El archivo subido es muy grande.')
    # Leer el archivo CSV
    data = file.read().decode('UTF-8').splitlines()
    try:
        reader = csv.DictReader(data)
        for index, container in enumerate(reader, start=1):
            valid, result = Container.validate_and_create({
                'code': container.get('Codigo'),
                'carrier': container.get('Empresa naviera'),
                'origin_name': container.get('Ubicacion de origen'),
                'origin_latitude': container.get('Latitud de origen (opcional)'),
                'origin_longitude': container.get('Longitud de origen (opcional)'),
                'destination_name': container.get('Ubicacion de destino'),
                'destination_latitude': container.get('Latitud de destino (opcional)'),
                'destination_longitude': container.get('Longitud de destino (opcional)')
            })
            if not valid:
                return RestResponse(True, 'Error al guardar el contenedor {}: {}'.format(index, result))
    except ValueError as ex:
        return RestResponse(True, 'Hubo un error al leer el archivo CSV.')
    # Obtener la lista de contenedores para guardar en base de datos
    return RestResponse(False, 'Contenedores marítimos insertados correctamente.')

def export_data(request):
    """Exporta en un archivo CSV el resultado de la búsqueda de contenedores."""
    # Preparar filtros, si no son válidos se mostará un mensaje de error en JSON
    valid, query = prepare_query(request.GET)
    if not valid:
        return reverse('container-index')
    # TODO: Implementar lógica para exportar lista de contenedores
    return HttpResponse('TODO: Exportar lista de contenedores')
