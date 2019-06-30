from django.forms.models import model_to_dict
from django.http import JsonResponse

from ..models import Location
from ..utils import RestResponse

TERM_MIN_LENGTH = 3

def search(request):
    # Obtener la cadena de búsqueda
    query = request.GET.get('term')
    if query is None:
        return JsonResponse({
            'error': True,
            'message': 'Ingrese una cadena de búsqueda.',
            'locations': []
        })
    if len(query) < TERM_MIN_LENGTH:
        return JsonResponse({
            'error': True,
            'message': 'La cadena de búsqueda debe ser de por lo menos {} caracteres.'.format(TERM_MIN_LENGTH),
            'locations': []
        })
    # Obtener las ubicaciones según la cadena de búsqueda
    locations = []
    for location in Location.objects.filter(name__icontains=query):
        locations.append(model_to_dict(location))
    # Devolver los valores en formato JSON
    return JsonResponse({
        'error': False,
        'message': None,
        'locations': locations
    })
