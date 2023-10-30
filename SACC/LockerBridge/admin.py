from django.contrib import admin
from .models import Reservation, CancelReservation, Client, Operator, Confirmed, Loaded, Retrieved

admin.site.register(Reservation)
admin.site.register(CancelReservation)
admin.site.register(Client)
admin.site.register(Operator)
admin.site.register(Confirmed)
admin.site.register(Loaded)
admin.site.register(Retrieved)

