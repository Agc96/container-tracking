from django.forms.models import model_to_dict
from django.http import JsonResponse

from ..models import Location

def search(request):
    error = True
    message = None
    locations = []
    try:
        # Obtener la cadena de búsqueda
        query = request.GET['term']
        assert len(query) > 2
        # Obtener las ubicaciones según la cadena de búsqueda
        for location in Location.objects.filter(name__icontains=query):
            locations.append(model_to_dict(location))
        error = False
    except AssertionError:
        message = 'La cadena de búsqueda debe ser de por lo menos 3 caracteres.'
    except KeyError:
        message = 'Ingrese una cadena de búsqueda.'
    # Devolver los valores en formato JSON
    return JsonResponse({
        'error': error,
        'message': message,
        'locations': locations
    })
