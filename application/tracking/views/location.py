from django.forms.models import model_to_dict
from django.http import JsonResponse

from ..models import Location
from ..utils import RestResponse

LOCATION_MIN_LENGTH = 3

def search(request):
    if not request.user.is_authenticated:
        return RestResponse(True, 'Debe iniciar sesión para continuar.', locations=[])
    # Obtener la cadena de búsqueda
    query = request.GET.get('term')
    if query is None:
        return RestResponse(True, 'Ingrese una cadena de búsqueda.', locations=[])
    if len(query) < LOCATION_MIN_LENGTH:
        message = 'La cadena de búsqueda debe ser de por lo menos {} caracteres.'.format(LOCATION_MIN_LENGTH)
        return RestResponse(True, message, locations=[])
    # Obtener las ubicaciones según la cadena de búsqueda
    locations = []
    for location in Location.objects.filter(name__icontains=query):
        locations.append(model_to_dict(location))
    # Devolver los valores en formato JSON
    return RestResponse(False, None, locations=locations)
