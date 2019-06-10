from django.db import models

CHAR_LENGTH_CONTAINER = 11
CHAR_LENGTH_SHORT     = 32
CHAR_LENGTH_NORMAL    = 64
CHAR_LENGTH_LARGE     = 128
DEFAULT_ON_DELETE     = models.CASCADE

"""
class User(models.Model):
    fullname = models.CharField(max_length=CHAR_LENGTH_NORMAL)
    email    = models.CharField(max_length=CHAR_LENGTH_NORMAL)
    role     = models.IntegerField()
    username = models.CharField(max_length=CHAR_LENGTH_SHORT)
    password = models.CharField(max_length=CHAR_LENGTH_LARGE)
"""

class Carrier(models.Model):
    name = models.CharField(max_length=CHAR_LENGTH_NORMAL)
    def __str__(self):
        return self.name

class Location(models.Model):
    name      = models.CharField(max_length=CHAR_LENGTH_NORMAL)
    latitude  = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.name

class Container(models.Model):
    code         = models.CharField(max_length=CHAR_LENGTH_CONTAINER)
    carrier      = models.ForeignKey(Carrier, on_delete=DEFAULT_ON_DELETE)
    origin       = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE, related_name="origin")
    destination  = models.ForeignKey(Location, on_delete=DEFAULT_ON_DELETE, related_name="destination")
    processed    = models.BooleanField(default=False)
    arrival_date = models.DateTimeField(default=None)
    def __str__(self):
        return self.code
