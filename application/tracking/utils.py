from django.http import JsonResponse

import datetime

# Constantes
PAGE_COUNT  = 10
DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M'

def add_to_query(request, query, request_key, filter_key, conversion=str, allow_nulls=True):
    try:
        # Obtener valor convertido del query
        request_value = parse_query(request, request_key, conversion)
        if request_value is None:
            return allow_nulls
        else:
            query[filter_key] = request_value # Colocar el valor en el query
            return True
    except ValueError:
        return False

def parse_query(request, key, conversion=str, default=None):
    # Obtener valor y verificar si está vacío
    value = request.get(key)
    if is_empty(value):
        return default
    # Convertir valor según la conversión especificada
    if conversion == datetime.date:
        return datetime.datetime.strptime(value, DATE_FORMAT)
    elif conversion == datetime.time:
        return datetime.datetime.strptime(value, TIME_FORMAT)
    elif conversion == datetime.datetime:
        return datetime.datetime.strptime(value, DATE_FORMAT + ' ' + TIME_FORMAT)
    else:
        return conversion(value)

def is_empty(value):
    return (value is None) or (isinstance(value, str) and len(value) <= 0)

def RestResponse(error, message, **kwargs):
    return JsonResponse({
        'error': error,
        'message': message
    })
