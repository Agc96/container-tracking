from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.utils import timezone

from .utils import DATETIME_FORMAT, parse_query, is_empty

import re

# Constantes para tipos de dato cadena
LENGTH_CONTAINER  = 11
LENGTH_SHORT      = 32
LENGTH_NORMAL     = 64
LENGTH_LARGE      = 128
DEFAULT_ON_DELETE = models.CASCADE
DEFAULT_STATUS    = 1 # Estado del contenedor: Pendiente

class Enterprise(models.Model):
    """Empresa dedicada al transporte marítimo. Puede ser una empresa de tercer partido (empresa naviera)."""
    name       = models.CharField(max_length=LENGTH_NORMAL)
    carrier    = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class Location(models.Model):
    """Ubicación de un puerto. Incluye datos de latitud y longitud."""
    name       = models.CharField(max_length=LENGTH_LARGE)
    latitude   = models.FloatField(default=None)
    longitude  = models.FloatField(default=None)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name
    @classmethod
    def validate_and_create(cls, data):
        # Validar el nombre de la ubicación
        name = parse_query(data, 'name')
        if is_empty(name):
            return False, 'Ingrese el nombre de la ubicación.'
        # Validar la latitud de la ubicación
        try:
            latitude = parse_query(data, 'latitude', float)
            if latitude is None:
                return False, 'Ingrese la latitud de la ubicación.'
        except ValueError:
            return False, 'La latitud de la ubicación no es válida.'
        # Validar la longitud de la ubicación
        try:
            longitude = parse_query(data, 'longitude', float)
            if longitude is None:
                return False, 'Ingrese la longitud de la ubicación.'
        except ValueError:
            return False, 'La longitud de la ubicación no es válida.'
        # Devolver una nueva instancia de la ubicación
        return True, cls.objects.create(name=name, latitude=latitude, longitude=longitude)
    @staticmethod
    def equals(first, second):
        return (first == second) or ((first.latitude == second.latitude) and (first.longitude == second.longitude))

class ContainerStatus(models.Model):
    name       = models.CharField(max_length=LENGTH_SHORT)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'tracking_container_status'

class Container(models.Model):
    code         = models.CharField(max_length=LENGTH_CONTAINER)
    carrier      = models.ForeignKey(Enterprise, on_delete=DEFAULT_ON_DELETE)
    origin       = models.ForeignKey(Location, default=None, on_delete=DEFAULT_ON_DELETE, related_name='origin')
    destination  = models.ForeignKey(Location, default=None, on_delete=DEFAULT_ON_DELETE, related_name='destination')
    arrival_date = models.DateTimeField(default=None)
    status       = models.ForeignKey(ContainerStatus, on_delete=DEFAULT_ON_DELETE, default=DEFAULT_STATUS)
    priority     = models.IntegerField(default=1)
    created_at   = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.code
    @classmethod
    def validate_and_create(cls, data):
        # Obtener el código del contenedor
        code = parse_query(data, 'code')
        if is_empty(code):
            return False, 'Ingrese el nombre del contenedor.'
        if (len(code) != LENGTH_CONTAINER) or not re.match('^[A-Za-z]{4}[0-9]{7}$', code):
            return False, 'El contenedor debe tener exactamente 4 letras y 7 cifras.'
        # Obtener la empresa naviera del contenedor
        try:
            carrier_id = parse_query(data, 'carrier_id', int)
            if carrier_id is None:
                carrier_name = parse_query(data, 'carrier')
                if is_empty(carrier_name):
                    return False, 'Ingrese el nombre de la empresa naviera del contenedor.'
                try:
                    carrier = Enterprise.objects.get(name__icontains=carrier_name, carrier=True)
                except ObjectDoesNotExist:
                    return False, 'No se encontró la empresa naviera del contenedor.'
                except MultipleObjectsReturned:
                    return False, 'Se encontraron varias empresas navieras con el nombre especificado.'
            else:
                carrier = Enterprise.objects.get(pk=carrier_id)
        except ValueError:
            return False, 'La empresa naviera ingresada no es válida.'
        # Obtener la ubicación de origen del contenedor
        origin_name = parse_query(data, 'origin_name')
        if is_empty(origin_name):
            return False, 'Ingrese la ubicación de origen del contenedor.'
        try:
            origin = Location.objects.get(name__iexact=origin_name)
        except MultipleObjectsReturned:
            return False, 'Se encontraron varias ubicaciones de origen para el contenedor.'
        except ObjectDoesNotExist:
            valid, origin = Location.validate_and_create({
                'name': origin_name,
                'latitude': data.get('origin_latitude'),
                'longitude': data.get('origin_longitude')
            })
            if not valid:
                return False, 'Error en la ubicación de origen: ' + origin
        # Obtener la ubicación de destino del contenedor
        destination_name = parse_query(data, 'destination_name')
        if is_empty(destination_name):
            return False, 'Ingrese la ubicación de destino del contenedor.'
        try:
            destination = Location.objects.get(name__iexact=destination_name)
        except MultipleObjectsReturned:
            return False, 'Se encontraron varias ubicaciones de destino para el contenedor.'
        except ObjectDoesNotExist:
            valid, destination = Location.validate_and_create({
                'name': destination_name,
                'latitude': data.get('destination_latitude'),
                'longitude': data.get('destination_longitude')
            })
            if not valid:
                return False, 'Error en la ubicación de destino: ' + destination
        # Validar que las dos ubicaciones no sean las mismas
        if Location.equals(origin, destination):
            return False, 'La ubicación de origen no puede ser igual a la ubicación de destino.'
        return True, cls.objects.create(code=code, carrier=carrier, origin=origin, destination=destination)
        # return True, 'Se creó correctamente el contenedor marítimo.'
    class Meta:
        ordering = ['-id']

class MovementStatus(models.Model):
    status     = models.IntegerField()
    name       = models.CharField(max_length=LENGTH_NORMAL)
    enterprise = models.ForeignKey(Enterprise, on_delete=DEFAULT_ON_DELETE)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'tracking_movement_status'

class Vehicle(models.Model):
    name       = models.CharField(max_length=LENGTH_SHORT)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class Movement(models.Model):
    container  = models.ForeignKey(Container, on_delete=DEFAULT_ON_DELETE)
    location   = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE)
    status     = models.ForeignKey(MovementStatus, on_delete=DEFAULT_ON_DELETE)
    date       = models.DateTimeField()
    vehicle    = models.ForeignKey(Vehicle, on_delete=DEFAULT_ON_DELETE, default=None)
    vessel     = models.CharField(max_length=LENGTH_NORMAL, default=None)
    voyage     = models.CharField(max_length=LENGTH_SHORT, default=None)
    estimated  = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return '{}: {} at {}'.format(self.container.name, self.status.name, self.date.strftime(DATETIME_FORMAT))
    class Meta:
        ordering = ['id', 'date']
