from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Reservation, CancelReservation, Client, Operator, Confirmed, Loaded, Retrieved


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'product_height', 'product_width']

class CancelReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelReservation
        fields = ['id', 'reservation']
    
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'mail']

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id', 'mail']

class ConfirmedSerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    operator = OperatorSerializer(read_only=True)
    class Meta:
        model = Confirmed
        fields = ['id', 'reservation', 'client', 'operator']

class LoadedSerializer(serializers.ModelSerializer):
    confirmed = ConfirmedSerializer(read_only=True)
    class Meta:
        model = Loaded
        fields = ['id', 'confirmed']

class RetrievedSerializer(serializers.ModelSerializer):
    confirmed = ConfirmedSerializer(read_only=True)
    class Meta:
        model = Retrieved
        fields = ['id', 'confirmed']




