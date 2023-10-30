from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Reservation, CancelReservation, Client, Operator, Confirmed, Loaded, Retrieved

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'mail']

class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = ['id', 'mail']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        client = ClientSerializer(read_only=True)
        operator = OperatorSerializer(read_only=True)
        model = Reservation
        fields = ['id', 'product_height', 'product_width', 'client', 'operator']

class CancelReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelReservation
        fields = ['id', 'reservation']

class ConfirmedSerializer(serializers.ModelSerializer):
    class Meta:
        reservation = ReservationSerializer(read_only=True)
        model = Confirmed
        fields = ['id', 'reservation']

class LoadedSerializer(serializers.ModelSerializer):
    class Meta:
        reservation = ReservationSerializer(read_only=True)
        model = Loaded
        fields = ['id', 'reservation']

class RetrievedSerializer(serializers.ModelSerializer):
    class Meta:
        reservation = ReservationSerializer(read_only=True)
        model = Retrieved
        fields = ['id', 'reservation']




