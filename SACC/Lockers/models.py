from django.db import models

class Station(models.Model):
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    region = models.CharField(max_length=200)

    def __str__(self):
        return f'Id: {self.id}, Address: {self.address}, City: {self.city}, Region: {self.region}'
    
class Locker(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    height = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    availability = models.BooleanField(default=True)
    reserved = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    loaded = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    locked = models.BooleanField(default=True)

    def __str__(self):
        return f'Id: {self.id}, Availability: {self.availability}, Reserved: {self.reserved}, Confirmed: {self.confirmed}, Loaded: {self.loaded}, Opened: {self.opened}, Locked: {self.locked}'
