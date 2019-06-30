from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.utils import timezone

from .utils import parse_query, is_empty

import re

# Constantes para tipos de dato cadena

LENGTH_CONTAINER  = 11
LENGTH_SHORT      = 32
LENGTH_NORMAL     = 64
LENGTH_LARGE      = 128
DEFAULT_ON_DELETE = models.CASCADE

# Modelos de la base de datos

class Carrier(models.Model):
    name       = models.CharField(max_length=LENGTH_NORMAL)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class Location(models.Model):
    name       = models.CharField(max_length=LENGTH_LARGE)
    latitude   = models.FloatField()
    longitude  = models.FloatField()
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

class Container(models.Model):
    code         = models.CharField(max_length=LENGTH_CONTAINER)
    carrier      = models.ForeignKey(Carrier, on_delete=DEFAULT_ON_DELETE)
    origin       = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE, related_name="origin")
    destination  = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE, related_name="destination")
    processed    = models.BooleanField(default=False)
    arrival_date = models.DateTimeField(default=None)
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
        carrier_name = parse_query(data, 'carrier')
        if is_empty(carrier_name):
            return False, 'Ingrese el nombre de la empresa naviera del contenedor.'
        try:
            carrier = Carrier.objects.get(name__icontains=carrier_name)
        except ObjectDoesNotExist:
            return False, 'No se encontró la empresa naviera del contenedor.'
        except MultipleObjectsReturned:
            return False, 'Se encontraron varias empresas navieras con el nombre especificado.'
        # Obtener la ubicación de origen del contenedor
        origin_name = parse_query(data, 'origin-name')
        if is_empty(origin_name):
            return False, 'Ingrese la ubicación de origen del contenedor.'
        try:
            origin = Location.objects.get(name__iexact=origin_name)
        except MultipleObjectsReturned:
            return False, 'Se encontraron varias ubicaciones de origen para el contenedor.'
        except ObjectDoesNotExist:
            valid, origin = Location.validate_and_create({
                'name': origin_name,
                'latitude': data.get('origin-latitude'),
                'longitude': data.get('origin-longitude')
            })
            if not valid:
                return False, 'Error en la ubicación de origen: ' + origin
        # Obtener la ubicación de destino del contenedor
        destination_name = parse_query(data, 'destination-name')
        if is_empty(destination_name):
            return False, 'Ingrese la ubicación de destino del contenedor.'
        try:
            destination = Location.objects.get(name__iexact=destination_name)
        except MultipleObjectsReturned:
            return False, 'Se encontraron varias ubicaciones de destino para el contenedor.'
        except ObjectDoesNotExist:
            valid, destination = Location.validate_and_create({
                'name': destination_name,
                'latitude': data.get('destination-latitude'),
                'longitude': data.get('origin-longitude')
            })
            if not valid:
                return False, 'Error en la ubicación de destino: ' + destination
        return True, cls.objects.create(code=code, carrier=carrier, origin=origin, destination=destination)
        # return True, 'Se creó correctamente el contenedor marítimo.'
    class Meta:
        ordering = ['-id']

# TODO: Borrar esto cuando se implemente el login y las sesiones

class MockUser:
    fullname = 'Anthony Gutiérrez'
    role = 'Administrador'
