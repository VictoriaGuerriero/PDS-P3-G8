from django.contrib.auth.models import User
from rest_framework import serializers

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'address', 'city', 'region']

class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        station = StationSerializer(read_only=True)
        model = Locker
        fields = ['id', 'station', 'height', 'width', 'availability', 'reserved', 'confirmed', 'loaded', 'opened', 'locked']
