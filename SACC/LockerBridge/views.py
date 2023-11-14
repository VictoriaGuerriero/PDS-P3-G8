from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

from .serializers import ReservationSerializer, ClientSerializer, OperatorSerializer, ConfirmedSerializer, LoadedSerializer, RetrievedSerializer
from .models import Reservation, CancelReservation, Client, Operator, Confirmed, Loaded, Retrieved
from Lockers.models import Locker, Station
from django.utils import timezone
import string
import random
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core import serializers
from django.core.mail import send_mail
from django.http import HttpResponse
import requests

def home(request):
    return render(request, 'home.html')

def generate_unique_code(lenght=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=lenght))


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request):

        #Get product height and width from request
        product_height = request.data['product_height']
        product_width = request.data['product_width']
        client_id = request.data['client']
        operator_id = request.data['operator']
        client = Client.objects.get(id=client_id)
        operator = Operator.objects.get(id=operator_id)

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
                code = unique_code,
                client = client,
                operator = operator,
                active = True
            )
            suitable_locker.availability = False
            suitable_locker.reserved = True
            suitable_locker.save()

            subject = 'Locker Reservation'
            message = f'The reservation of the locker has been made successfully. Your code is {unique_code}. The locker is located in {suitable_locker.station.address} and its locker number is {suitable_locker.id}'
            from_email = 'notification@miuandes.cl'
            recipient_list = [operator.mail, client.mail]
            send_mail(subject, message, from_email, recipient_list)

            client_data = serializers.serialize('json', [client])
            operator_data = serializers.serialize('json', [operator])
            return JsonResponse({'id': reservation.id, 'code': unique_code, 'locker': suitable_locker.id, 'station': suitable_locker.station.id, 'client': client_data, 'operator': operator_data, 'active': reservation.active}, status=201)

    # @action(
    #     detail=True,
    #     methods=['post']
    # )
    def verify_operator(self, request):
        code = request.data['code']
        op_email = request.data['op_email']

        operator = Operator.objects.filter(mail=op_email).first()
        reservation = Reservation.objects.filter(code=code).first()
        if reservation and operator == reservation.operator:
            locker = reservation.locker
            locker.locked = False
            locker.opened = True
            locker.save()
            return JsonResponse({'message': 'Operator confirmed, locker opened'}, status=200)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)
        
    def verify_client(self, request):
        code = request.data['code']
        client_email = request.data['client_email']

        client = Client.objects.filter(mail=client_email).first()
        reservation = Reservation.objects.filter(code=code).first()
        if reservation and client == reservation.client:
            locker = reservation.locker
            locker.locked = False
            locker.opened = True
            locker.save()

            return JsonResponse({'message': 'Client confirmed, locker opened and package retrieved'}, status=200)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)
    
        
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
        reservation = Reservation.objects.get(id=reservation_id)
        if reservation:
            Confirmed.objects.create(
                reservation=reservation,
            )
            locker = reservation.locker
            locker.confirmed = True
            locker.save()
            return JsonResponse({'message': 'Size confirmed'}, status=201)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)

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

    def create(self, request):
        # code = request.data['code']
        # op_email = request.data['op_email']
        # operator = Operator.objects.filter(mail=op_email).first()
        # reservation_id = request.data['reservation_id']
        # reservation = Reservation.objects.get(id=reservation_id)
        locker_id = request.data['locker_id']
        locker = Locker.objects.get(id=locker_id)
        reservation = Reservation.objects.filter(locker=locker, active=True).first()
        if reservation:
            Loaded.objects.create(
                reservation=reservation,
            )
            subject = 'Locker Loaded'
            message = 'Your package is ready to be retrieved'
            from_email = 'notification@miuandes.cl'
            recipient_list = [reservation.client.mail]

            send_mail(subject, message, from_email, recipient_list)
            locker = reservation.locker
            locker.loaded = True
            locker.opened = False
            locker.locked = True
            locker.save()
            return JsonResponse({'message': 'Locker Loaded Correctly'}, status=200)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)

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

    # @action(
    #     detail=True,
    #     methods=['post']
    # )
    def create(self, request):
        locker_id = request.data['locker_id']
        locker = Locker.objects.get(id=locker_id)
        reservation = Reservation.objects.filter(locker=locker, active=True).first()
        if reservation:
            Retrieved.objects.create(
                reservation=reservation,
            )
            subject = 'Package Retrieved'
            message = 'The package has been retrieved'
            from_email = 'notification@miuandes.cl'
            recipient_list = [reservation.operator.mail]

            send_mail(subject, message, from_email, recipient_list)
            locker = reservation.locker
            locker.availability = True
            locker.reserved = False
            locker.confirmed = False
            locker.loaded = False
            locker.opened = False
            locker.locked = True
            locker.save()
            reservation.active = False
            reservation.save()
            return JsonResponse({'message': 'Packaged retrieved by client'}, status=200)
        else:
            return JsonResponse({'message': 'Reservation not found'}, status=404)

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
    
################################################## FRONT ##################################################

                                       
                                    
from .forms import ReservationForm

def operator_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save to database)
            email = form.cleaned_data['email']
            reservation_code = form.cleaned_data['reservation_code']
            
            data = {
                'code': reservation_code,
                'op_email': email
            }

            response = requests.post('https://tsqrmn8j-8000.brs.devtunnels.ms/api/reservations/verify-operator/', data=data)

            if response.status_code == 200:
                messages.success(request, f'Success! Operator confirmed, locker opened. Response: {response.json()}')
            else:
                messages.error(request, f'Error! {response.json()}')

            return redirect('operator_view')


    else:
        form = ReservationForm()

    return render(request, 'operator_form.html', {'form': form})

def client_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save to database)
            email = form.cleaned_data['email']
            reservation_code = form.cleaned_data['reservation_code']
            
            data = {
                'code': reservation_code,
                'client_email': email
            }

            response = requests.post('https://tsqrmn8j-8000.brs.devtunnels.ms/api/reservations/verify-client/', data=data)

            if response.status_code == 200:
                messages.success(request, f'Success! Client confirmed, locker opened. Response: {response.json()}')
            else:
                messages.error(request, f'Error! {response.json()}')
            
            return redirect('operator_view')
    else:
        form = ReservationForm()

    return render(request, 'client_form.html', {'form': form})