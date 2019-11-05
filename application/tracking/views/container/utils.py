from ...utils import add_to_query

import datetime

def prepare_query(request):
    """Función auxiliar para traducir los filtros agregados por el usuario a queries de base de datos."""
    query = {}
    # Agregar filtro por código del contenedor
    add_to_query(request, query, 'code', 'code__icontains')
    # Agregar filtro por empresa naviera que transporta al contenedor
    if not add_to_query(request, query, 'carrier', 'carrier__id', int):
        return False, 'Seleccione una empresa naviera válida.'
    # Agregar filtro por ubicación de origen del contenedor
    add_to_query(request, query, 'origin', 'origin__name__icontains')
    # Agregar filtro por ubicación de destino del contenedor
    add_to_query(request, query, 'destination', 'destination__name__icontains')
    # Agregar filtro por fecha de registro mínima del contenedor
    if not add_to_query(request, query, 'since', 'created_at__gte', datetime.date):
        return False, 'La fecha de registro mínima debe tener el formato dd/mm/aaaa.'
    # Agregar filtro por fecha de registro máxima del contenedor
    if not add_to_query(request, query, 'until', 'created_at__lte', datetime.date):
        return False, 'La fecha de registro máxima debe tener el formato dd/mm/aaaa.'
    # Agregar filtro por estado del contenedor
    if not add_to_query(request, query, 'status', 'status__id', int):
        return False, 'Seleccione un estado de contenedor válido.'
    # Si no hubo error alguno, devuelve NULL.
    return True, query
