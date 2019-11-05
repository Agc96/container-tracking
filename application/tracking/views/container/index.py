from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .utils import prepare_query
from ...models import Enterprise, Container, ContainerStatus
from ...utils import parse_query, RestResponse, PAGE_COUNT

def index(request):
    """Renderiza la pantalla de búsqueda y listado de contenedores marítimos."""
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'tracking/container/index.html', {
        'fullname': request.user.first_name + ' ' + request.user.last_name,
        'carriers': Enterprise.objects.filter(carrier=True),
        'statuses': ContainerStatus.objects.all()
    })

def search(request):
    """Obtiene según los filtros brindados los resultados de la búsqueda de contenedores."""
    if not request.user.is_authenticated:
        return RestResponse(True, 'Debe iniciar sesión para continuar.')
    # Preparar filtros, si no son válidos se mostará un mensaje de error en JSON
    valid, query = prepare_query(request.GET)
    if not valid:
        return RestResponse(True, query)
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
        container_json['origin'] = container_db.origin.name if container_db.origin else None
        container_json['destination'] = container_db.destination.name if container_db.destination else None
        container_json['status_name'] = container_db.status.name
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
