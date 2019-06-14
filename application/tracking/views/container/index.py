from django.http import HttpResponse
from django.shortcuts import render

from ...models import Carrier, MockUser

def index(request):
    """Búsqueda y listado de contenedores marítimos."""
    return render(request, 'tracking/container/index.html', {
        'user': MockUser(),
        'carriers': Carrier.objects.all()
    })

def search(request):
    return HttpResponse('TODO: Busqueda y paginado de contenedores')

def import_data(request):
    # TODO: Implementar lógica para importar lista de contenedores
    return HttpResponse('TODO: Importar lista de contenedores')

def export_data(request):
    # TODO: Implementar lógica para exportar lista de contenedores
    return HttpResponse('TODO: Exportar lista de contenedores')
