from django.db import models

LENGTH_CONTAINER  = 11
LENGTH_SHORT      = 32
LENGTH_NORMAL     = 64
LENGTH_LARGE      = 128
DEFAULT_ON_DELETE = models.CASCADE

# Modelos de la base de datos

class Carrier(models.Model):
    name = models.CharField(max_length=LENGTH_NORMAL)
    def __str__(self):
        return self.name

class Location(models.Model):
    name      = models.CharField(max_length=LENGTH_LARGE)
    latitude  = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.name

class Container(models.Model):
    code         = models.CharField(max_length=LENGTH_CONTAINER)
    carrier      = models.ForeignKey(Carrier, on_delete=DEFAULT_ON_DELETE)
    origin       = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE, related_name="origin")
    destination  = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE, related_name="destination")
    processed    = models.BooleanField(default=False)
    arrival_date = models.DateTimeField(default=None)
    def __str__(self):
        return self.code

# TODO: Borrar esto cuando se implemente el login y las sesiones
class MockUser:
    fullname = 'Anthony Gutiérrez'
    role = 'Administrador'
