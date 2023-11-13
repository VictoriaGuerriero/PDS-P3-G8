from django.db import models

class Client(models.Model):
    mail = models.CharField(max_length=200)

    def __str__(self):
        return f'Id: {self.id}, Mail: {self.mail}'

class Operator(models.Model):
    mail = models.CharField(max_length=200)

    def __str__(self):
        return f'Id: {self.id}, Mail: {self.mail}'
    
class Reservation(models.Model):
    reservation_date = models.DateTimeField(auto_now_add=True)
    product_height = models.IntegerField(default=0)
    product_width = models.IntegerField(default=0)
    locker = models.ForeignKey('Lockers.Locker', on_delete=models.CASCADE)
    station = models.ForeignKey('Lockers.Station', on_delete=models.CASCADE)
    code = models.CharField(max_length=200, default='')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Id: {self.id}, Reservation Date: {self.reservation_date}, Product Height: {self.product_height}, Product Width: {self.product_width}, Locker: {self.locker}, Station: {self.station}, Client: {self.client}, Operator: {self.operator}'

class CancelReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    code = models.CharField(max_length=200, default='')
    cancel_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Reservation: {self.reservation}, Cancel Date: {self.cancel_date}'

class Confirmed(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    confirmation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Reservation: {self.reservation}, Confirmation Date: {self.confirmation_date}'
    
class Loaded(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    load_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Reservation: {self.reservation}, Load Date: {self.load_date}'
    
class Retrieved(models.Model): 
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    retrieved_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Id: {self.id}, Reservation: {self.reservation}, Retrieved Date: {self.retrieved_date}'

