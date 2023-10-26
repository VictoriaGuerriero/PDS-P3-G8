from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from .serializers import StationSerializer, LockerSerializer
from .models import Station, Locker
from django.http import JsonResponse


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_station(self, request, pk):
        station = Station.objects.get(id=pk)
        station.delete()
        return JsonResponse({'message': 'Station deleted'}, status=200)
    
class LockerViewSet(viewsets.ModelViewSet):
    queryset = Locker.objects.all()
    serializer_class = LockerSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_locker(self, request, pk):
        locker = Locker.objects.get(id=pk)
        locker.delete()
        return JsonResponse({'message': 'Locker deleted'}, status=200)

    

# Create your views here.
