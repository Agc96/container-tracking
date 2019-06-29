from django.http import JsonResponse

import datetime

DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT

def add_to_query(request, query, request_key, filter_key, conversion=str):
    request_value = request.GET.get(request_key)
    if (request_value is not None) and (len(request_value) > 0):
        try:
            if conversion == datetime.date:
                query[filter_key] = datetime.datetime.strptime(request_value, DATE_FORMAT)
            elif conversion == datetime.time:
                query[filter_key] = datetime.datetime.strptime(request_value, TIME_FORMAT)
            elif conversion == datetime.datetime:
                query[filter_key] = datetime.datetime.strptime(request_value, DATETIME_FORMAT)
            else:
                query[filter_key] = conversion(request_value)
        except ValueError:
            return False
    return True

def rest_response(error, message, **kwargs):
    kwargs['error'] = error
    kwargs['message'] = message
    return JsonResponse(kwargs)
