from django.db import models

CHAR_LENGTH_CONTAINER = 11
CHAR_LENGTH_SHORT     = 32
CHAR_LENGTH_NORMAL    = 64
CHAR_LENGTH_LARGE     = 128
DEFAULT_ON_DELETE     = models.CASCADE

class User(models.Model):
    fullname = models.CharField(max_length = CHAR_LENGTH_NORMAL)
    email    = models.CharField(max_length = CHAR_LENGTH_NORMAL)
    role     = models.IntegerField()
    username = models.CharField(max_length = CHAR_LENGTH_SHORT)
    password = models.CharField(max_length = CHAR_LENGTH_LARGE)

class Carrier(models.Model):
    name = models.CharField(max_length = CHAR_LENGTH_NORMAL)

class Location(models.Model):
    name      = models.CharField(max_length = CHAR_LENGTH_NORMAL)
    latitude  = models.FloatField()
    longitude = models.FloatField()

class Container(models.Model):
    code         = models.CharField(max_length = CHAR_LENGTH_CONTAINER)
    carrier      = models.ForeignKey(Carrier, on_delete = DEFAULT_ON_DELETE)
    origin       = models.ForeignKey(Location, related_name = "origin", on_delete = DEFAULT_ON_DELETE)
    destination  = models.ForeignKey(Location, related_name = "destination", on_delete = DEFAULT_ON_DELETE)
    processed    = models.BooleanField(default = False)
    arrival_date = models.DateTimeField(default = None)
