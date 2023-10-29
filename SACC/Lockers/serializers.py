from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Station, Locker

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'address', 'city', 'region']

class LockerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        station = StationSerializer(read_only=True)
        model = Locker
        fields = ['id', 'station', 'height', 'width']

class LockerRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        station = StationSerializer(read_only=True)
        model = Locker
        fields = '__all__'
