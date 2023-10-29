from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets
from .serializers import StationSerializer, LockerCreateSerializer, LockerRetrieveSerializer
from rest_framework.response import Response
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
    serializer_class = LockerRetrieveSerializer

    @action(
            detail=True, 
            methods=['get']
            )
    def get_all_lockers(self, request):
        lockers = Locker.objects.all()
        serializer = LockerRetrieveSerializer(lockers, many=True)
        return Response(serializer.data)
    
    @action(
            detail=True, 
            methods=['get']
            )
    def get_lockers_by_station(self, request, pk):
        lockers = Locker.objects.filter(station=pk)
        serializer = LockerRetrieveSerializer(lockers, many=True)
        return Response(serializer.data)
    
    @action(
            detail=True, 
            methods=['put']
            )
    def update_opened(self, request, pk):
        locker = Locker.objects.get(id=pk)
        locker.opened = True
        locker.save()
        return JsonResponse({'message': 'Locker opened'}, status=200)
    
    @action(
            detail=True, 
            methods=['put']
            )
    def update_locked(self, request, pk):
        locker = Locker.objects.get(id=pk)
        locker.locked = True
        locker.save()
        return JsonResponse({'message': 'Locker locked'}, status=200)
    
    @action(
            detail=True, 
            methods=['put']
            )
    def update_loaded(self, request, pk):
        locker = Locker.objects.get(id=pk)
        locker.loaded = True
        locker.save()
        return JsonResponse({'message': 'Locker loaded'}, status=200)

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_locker(self, request, pk):
        locker = Locker.objects.get(id=pk)
        locker.delete()
        return JsonResponse({'message': 'Locker deleted'}, status=200)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LockerCreateSerializer
        return super().get_serializer_class()