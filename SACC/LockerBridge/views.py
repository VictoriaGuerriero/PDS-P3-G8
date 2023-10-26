from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from SACC.LockerBridge.serializers import ReservationSerializer, ClientSerializer, OperatorSerializer, ConfirmedSerializer, LoadedSerializer, RetrievedSerializer
from .models import Reservation, CancelReservation, Client, Operator, Confirmed, Loaded, Retrieved
from Lockers.models import Locker, Station
from django.utils import timezone
import string
import random
from rest_framework import viewsets
from rest_framework.decorators import action

def generate_unique_code(lenght=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=lenght))


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @action(
        detail=True, 
        methods=['post']
    )
    def create_reservation(self, request, pk):

        #Get product height and width from request
        product_height = request.data['product_height']
        product_width = request.data['product_width']

        suitable_locker = Locker.objects.filter(
                height__gte=product_height,
                width__gte=product_width,
                station__id=pk,
                status='available'
        ).first()

        if suitable_locker is None:
            return JsonResponse({'message': 'No suitable locker available'}, status=404)
        else:
            unique_code = generate_unique_code()
            reservation = Reservation.objects.create(
                product_height=product_height,
                product_width=product_width,
                locker=suitable_locker,
                station=suitable_locker.station,
                code = unique_code
            )
            Locker.objects.filter(id=suitable_locker.id).update(reserved=True)
            return JsonResponse({'id': reservation.id}, status=201)
        
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_client(self, request, pk):
        client = Client.objects.get(id=pk)
        client.delete()
        return JsonResponse({'message': 'Client deleted'}, status=200)
    
class OperatorViewSet(viewsets.ModelViewSet):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_operator(self, request, pk):
        operator = Operator.objects.get(id=pk)
        operator.delete()
        return JsonResponse({'message': 'Operator deleted'}, status=200)
    
class ConfirmedViewSet(viewsets.ModelViewSet):
    queryset = Confirmed.objects.all()
    serializer_class = ConfirmedSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_confirmed(self, request, pk):
        confirmed = Confirmed.objects.get(id=pk)
        confirmed.delete()
        return JsonResponse({'message': 'Confirmed deleted'}, status=200)
    
class LoadedViewSet(viewsets.ModelViewSet):
    queryset = Loaded.objects.all()
    serializer_class = LoadedSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_loaded(self, request, pk):
        loaded = Loaded.objects.get(id=pk)
        loaded.delete()
        return JsonResponse({'message': 'Loaded deleted'}, status=200)
    
class RetrievedViewSet(viewsets.ModelViewSet):
    queryset = Retrieved.objects.all()
    serializer_class = RetrievedSerializer

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_retrieved(self, request, pk):
        retrieved = Retrieved.objects.get(id=pk)
        retrieved.delete()
        return JsonResponse({'message': 'Retrieved deleted'}, status=200)


