from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from ...models import Carrier, Container, MockUser
from ...utils import add_to_query, parse_query, RestResponse, is_empty, PAGE_COUNT

import csv
import datetime
import io

def index(request):
    """Renderiza la pantalla de búsqueda y listado de contenedores marítimos."""
    return render(request, 'tracking/container/index.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all()
    })

def search(request):
    """Obtiene según los filtros brindados los resultados de la búsqueda de contenedores."""
    # Preparar filtros, si no son válidos se mostará un mensaje de error en JSON
    valid, query = prepare_query(request.GET)
    if not valid:
        return query
    # Preparar paginación
    cursor = Container.objects.filter(**query)
    paginator = Paginator(cursor, PAGE_COUNT)
    try:
        page = paginator.get_page(parse_query(request.GET, 'page', int, 1))
    except ValueError:
        return RestResponse(True, 'Ingrese un número de página válido.')
    # Preparar datos de los contenedores
    containers = []
    for container_db in page.object_list:
        container_json = model_to_dict(container_db)
        container_json['carrier'] = container_db.carrier.name
        container_json['origin'] = container_db.origin.name
        container_json['destination'] = container_db.destination.name
        container_json['url'] = reverse('container-detail', args=[container_db.id])
        containers.append(container_json)
    # Devolver los datos
    return JsonResponse({
        'error': False,
        'message': None,
        'containers': containers,
        'count': paginator.count,
        'page': page.number,
        'pagecount': paginator.num_pages
    })

def prepare_query(request):
    """Función auxiliar para traducir los filtros agregados por el usuario a queries de base de datos."""
    query = {}
    # Agregar filtro por código del contenedor
    add_to_query(request, query, 'code', 'code__icontains')
    # Agregar filtro por empresa naviera que transporta al contenedor
    if not add_to_query(request, query, 'carrier', 'carrier__id', int):
        return False, RestResponse(True, 'Seleccione una empresa naviera válida.')
    # Agregar filtro por ubicación de origen del contenedor
    add_to_query(request, query, 'origin', 'origin__name__icontains')
    # Agregar filtro por ubicación de destino del contenedor
    add_to_query(request, query, 'destination', 'destination__name__icontains')
    # Agregar filtro por fecha de registro mínima del contenedor
    if not add_to_query(request, query, 'since', 'created_at__gte', datetime.date):
        return False, RestResponse(True, 'La fecha de registro mínima debe tener el formato dd/mm/aaaa.')
    # Agregar filtro por fecha de registro máxima del contenedor
    if not add_to_query(request, query, 'until', 'created_at__lte', datetime.date):
        return False, RestResponse(True, 'La fecha de registro máxima debe tener el formato dd/mm/aaaa.')
    # Si no hubo error alguno, devuelve NULL.
    return True, query

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
                'origin-name': container.get('Ubicacion de origen'),
                'origin-latitude': container.get('Latitud de origen (opcional)'),
                'origin-longitude': container.get('Longitud de origen (opcional)'),
                'destination-name': container.get('Ubicacion de destino'),
                'destination-latitude': container.get('Latitud de destino (opcional)'),
                'destination-longitude': container.get('Longitud de destino (opcional)')
            })
            if not valid:
                return RestResponse(True, 'Error al guardar el contenedor {}: {}'.format(index, result))
    except ValueError as ex:
        return RestResponse(True, 'Hubo un error al leer el archivo CSV.')
    # Obtener la lista de contenedores para guardar en base de datos
    return RestResponse(False, 'Contenedores marítimos insertados correctamente.')

def validate_import_value(container, data, container_attr, data_key):
    # Verificar que el valor existe
    data_value = data.get(data_key)
    if is_empty(data_value):
        return False
    # Guardar el valor en el objeto de base de datos
    setattr(container, container_attr, data_value)
    return True

def export_data(request):
    """Exporta en un archivo CSV el resultado de la búsqueda de contenedores."""
    # Preparar filtros, si no son válidos se mostará un mensaje de error en JSON
    valid, query = prepare_query(request.GET)
    if not valid:
        return reverse('container-index')
    # TODO: Implementar lógica para exportar lista de contenedores
    return HttpResponse('TODO: Exportar lista de contenedores')
