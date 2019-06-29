from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from ...models import Carrier, Container, MockUser
from ..utils import add_to_query, rest_response

import datetime

def index(request):
    """Búsqueda y listado de contenedores marítimos."""
    return render(request, 'tracking/container/index.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all()
    })

def search(request):
    query = {}
    # Filtro por código del contenedor
    add_to_query(request, query, 'code', 'code__icontains')
    # Filtro por empresa naviera
    if not add_to_query(request, query, 'carrier', 'carrier__id', int):
        return rest_response(True, 'Seleccione una empresa naviera válida.', containers=[])
    # Filtro por ubicación de origen
    add_to_query(request, query, 'origin', 'origin__name__icontains')
    # Filtro por ubicación de destino
    add_to_query(request, query, 'destination', 'destination__name__icontains')
    # Filtro por fecha inicial de registro
    if not add_to_query(request, query, 'since', 'created_at__gte', datetime.date):
        return rest_response(True, 'La fecha de registro mínima debe tener el formato dd/mm/aaaa.', containers=[])
    # Filtro por fecha final de registro
    if not add_to_query(request, query, 'until', 'created_at__lte', datetime.date):
        return rest_response(True, 'La fecha de registro máxima debe tener el formato dd/mm/aaaa.', containers=[])
    # Preparar datos de los contenedores
    containers = []
    cursor = Container.objects.filter(**query)
    for container in cursor:
        containers.append(model_to_dict(container))
    # Devolver los datos
    return rest_response(False, None, containers=containers)

def import_data(request):
    # TODO: Implementar lógica para importar lista de contenedores
    return HttpResponse('TODO: Importar lista de contenedores')

def export_data(request):
    # TODO: Implementar lógica para exportar lista de contenedores
    return HttpResponse('TODO: Exportar lista de contenedores')
