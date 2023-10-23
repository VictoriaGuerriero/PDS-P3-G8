from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Reservation, CancelReservation, Client, Operator, Confirmed, Loaded, Retrieved


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'reservation_date', 'product_height', 'product_width', 'locker', 'station', 'status']

class CancelReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id']
    
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'mail']

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id', 'mail']

class ConfirmedReservationSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    operator = OperatorSerializer(read_only=True)
    class Meta:
        model = Confirmed
        fields = ['id', 'reservation', 'client', 'operator', 'confirmation_date']

class LoadedSerializer(serializers.ModelSerializer):
    confirmed = ConfirmedReservationSerializer(read_only=True)
    class Meta:
        model = Loaded
        fields = ['id', 'confirmed', 'load_date']

class RetrievedSerializer(serializers.ModelSerializer):
    confirmed = ConfirmedReservationSerializer(read_only=True)
    class Meta:
        model = Retrieved
        fields = ['id', 'confirmed', 'retrieved_date']




