from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .serializers import ReservationSerializer, ClientSerializer, OperatorSerializer, ConfirmedSerializer, LoadedSerializer, RetrievedSerializer
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

    def create(self, request):

        #Get product height and width from request
        product_height = request.data['product_height']
        product_width = request.data['product_width']

        suitable_locker = Locker.objects.filter(
                height__gte=product_height,
                width__gte=product_width,
                availability=True
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
            suitable_locker.availability = False
            suitable_locker.reserved = True
            suitable_locker.save()
            return JsonResponse({'id': reservation.id, 'code': unique_code, 'locker': suitable_locker.id, 'station': suitable_locker.station.id}, status=201)
        
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

    def create(self, request):
        reservation_id = request.data['reservation_id']
        client_id = request.data['client_id']
        operator_id = request.data['operator_id']
        reservation = Reservation.objects.get(id=reservation_id)
        client = Client.objects.get(id=client_id)
        operator = Operator.objects.get(id=operator_id)
        Confirmed.objects.create(
            reservation=reservation,
            client=client,
            operator=operator
        )
        reservation.confirmed = True
        reservation.save()
        return JsonResponse({'message': 'Reservation confirmed'}, status=201)

    @action(
        detail=True, 
        methods=['delete']
    )
    def delete_confirmed(self, request, pk):
        confirmed = Confirmed.objects.get(id=pk)
        confirmed.delete()
        return JsonResponse({'message': 'Confirmed deleted'}, status=200)
    
    @action(
        detail=True,
        methods=['post']
    )
    def verify_operator(self, request):
        code = request.data['code']
        op_email = request.data['op_email']
        operator = Operator.objects.filter(mail=op_email).first()
        reservation = Reservation.objects.filter(code=code).first()
        if reservation and operator:
            return JsonResponse({'id': reservation.id, 'code': code, 'locker': reservation.locker.id, 'station': reservation.station.id}, status=200)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)
        
    @action(
        detail=True,
        methods=['post']
    )
    def verify_client(self, request):
        code = request.data['code']
        client_email = request.data['client_email']
        client = Client.objects.filter(mail=client_email).first()
        reservation = Reservation.objects.filter(code=code).first()
        if reservation and client:
            return JsonResponse({'id': reservation.id, 'code': code, 'locker': reservation.locker.id, 'station': reservation.station.id}, status=200)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)
    
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
    
class CancelReservationViewSet(viewsets.ModelViewSet):
    queryset = CancelReservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request):

        reservation_id = request.data['reservation_id']
        reservation = Reservation.objects.get(id=reservation_id)
        locker = reservation.locker
        locker.availability = True
        locker.reserved = False
        locker.save()
        CancelReservation.objects.create(
            reservation=reservation,
            code=reservation.code
        )
        reservation.delete()
        return JsonResponse({'message': 'Reservation cancelled'}, status=201)