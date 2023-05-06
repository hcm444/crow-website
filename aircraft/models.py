from django.db import models

class Aircraft(models.Model):
    icao24 = models.CharField(max_length=100)
    callsign = models.CharField(max_length=100, blank=True, null=True)
    origin_country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    velocity = models.FloatField()
    heading = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
