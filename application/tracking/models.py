from django.db import models
from django.utils import timezone

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
    @staticmethod
    def validate_code(code):
        return (code != None) and (len(code) == LENGTH_CONTAINER) and re.match('^[A-Za-z]{4}[0-9]{7}$', code)

# TODO: Borrar esto cuando se implemente el login y las sesiones

class MockUser:
    fullname = 'Anthony Gutiérrez'
    role = 'Administrador'
