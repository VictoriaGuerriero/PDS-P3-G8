from django.db import models

class Reservation(models.Model):
    reservation_date = models.DateTimeField(auto_now_add=True)
    product_height = models.IntegerField(default=0)
    product_width = models.IntegerField(default=0)
    locker = models.ForeignKey('Lockers.Locker', on_delete=models.CASCADE)
    station = models.ForeignKey('Lockers.Station', on_delete=models.CASCADE)
    status = models.CharField(max_length=200, default='pending')

    def __str__(self):
        return f'Id: {self.id}, Reservation Date: {self.reservation_date}, Product Height: {self.product_height}, Product Width: {self.product_width}, Locker: {self.locker}, Station: {self.station}, Status: {self.status}'

class CancelReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    def __str__(self):
        return f'Id: {self.id}, Reservation: {self.reservation}'

class Client(models.Model):
    mail = models.CharField(max_length=200)

    def __str__(self):
        return f'Id: {self.id}, Mail: {self.mail}'

class Operator(models.Model):
    mail = models.CharField(max_length=200)

    def __str__(self):
        return f'Id: {self.id}, Mail: {self.mail}'

class Confirmed(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    confirmation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Reservation: {self.reservation}, Client: {self.client}, Operator: {self.operator}, Confirmation Date: {self.confirmation_date}'
    
class Loaded(models.Model):
    confirmed = models.ForeignKey(Confirmed, on_delete=models.CASCADE)
    load_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Confirmed: {self.confirmed}, Load Date: {self.load_date}'
    
class Retrieved(models.Model): 
    confirmed = models.ForeignKey(Confirmed, on_delete=models.CASCADE)
    retrieved_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Confirmed: {self.confirmed}, Retrieved Date: {self.retrieved_date}'
# Create your models here.
