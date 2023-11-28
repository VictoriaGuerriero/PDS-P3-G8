from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Avg
from django.db.models import Q
from django.db.models import F

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

def translate_json654(data):
    for i in range(3):
        casillero_id = data[i].get('id')
        disponible = data[i].get('disponible')
        abierto = data[i].get('abierto')

        if casillero_id in [1,2,3]:
            locker = Locker.objects.get(id=casillero_id)
            if disponible == "D":
                data[i]['availability'] = True
                data[i]['reserved'] = False
                data[i]['confirmed'] = False
                data[i]['loaded'] = False
                locker.availability = True
                locker.reserved = False
                locker.confirmed = False
                locker.loaded = False
                locker.save()
            elif disponible == "R":
                data[i]['availability'] = False
                data[i]['reserved'] = True
                data[i]['confirmed'] = False
                data[i]['loaded'] = False
                locker.availability = False
                locker.reserved = True
                locker.confirmed = False
                locker.loaded = False
                locker.save()
            elif disponible == "C":
                data[i]['availability'] = False
                data[i]['reserved'] = False
                data[i]['confirmed'] = True
                data[i]['loaded'] = False
                locker.availability = False
                locker.reserved = False
                locker.confirmed = True
                locker.loaded = False
                locker.save()
            elif disponible == "A":
                data[i]['availability'] = False
                data[i]['reserved'] = False
                data[i]['confirmed'] = False
                data[i]['loaded'] = True
                locker.availability = False
                locker.reserved = False
                locker.confirmed = False
                locker.loaded = True
                locker.save()

            if abierto == True:
                data[i]['locked'] = False
            elif abierto == False:
                data[i]['locked'] = True

            data[i]['height'] = 26.0
            data[i]['width'] = 43.0

            data[i].pop('disponible', None)
            data[i].pop('abierto', None)
            data[i].pop('o_email', None)
            data[i].pop('r_email', None)
            data[i].pop('r_username', None)
            data[i].pop('o_name', None)
            data[i].pop('tamano', None)

    return data


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

         #get lockers from another db
        response = requests.get('http://161.35.0.111:8000/api/casilleros_disponibles/')
        print(response.json())


        if response.status_code == 200:
            data = translate_json654(response.json())
            print(data)

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

            if suitable_locker.station.id == 1:
                print('station 1')
                json_data = {
                    'disponible': 'R',
                    'abierto': False
                }
                headers = {'Content-Type': 'application/json',
                        }

                print(suitable_locker.id)
                response = requests.post(f'http://161.35.0.111:8000/api/casilleros/actualizar/{suitable_locker.id}/', json=json_data, headers=headers)
                print(response.status_code)

            #operator mail

            subject = 'Locker Reservation'
            message = f'The reservation of the locker has been made successfully. The reservation code is {unique_code}. \n The locker is located in: {suitable_locker.station.address}. \n Its locker number is: {suitable_locker.id}. \n When at the station, please confirm that the package fits in the locker before leaving it at the following link: https://tsqrmn8j-8000.brs.devtunnels.ms/confirm-locker/ \n \n SACC Team'
            from_email = 'notification@miuandes.cl'
            recipient_list = [operator.mail]
            send_mail(subject, message, from_email, recipient_list)
            print(f'Email sent to operator ({operator.mail})')

            #client mail

            # subject = 'Locker Reservation'
            # message = f'The reservation of the locker has been made successfully. Your code is {unique_code}. \n The locker is located in: {suitable_locker.station.address}. \n Its locker number is: {suitable_locker.id}. \nWhen retrieving the package please enter the correct information in the following link: https://tsqrmn8j-8000.brs.devtunnels.ms/client/ \n \n SACC Team'
            # from_email = 'notification@miuandes.cl'
            # recipient_list = [client.mail]
            # send_mail(subject, message, from_email, recipient_list)
            # print(f'Email sent to client ({client.mail})')

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
        code = request.data['code']
        reservation = Reservation.objects.filter(code=code).first()
        if reservation:
            Confirmed.objects.create(
                reservation=reservation,
            )
            locker = reservation.locker
            locker.confirmed = True
            locker.save()

            #send mail to operator
            subject = 'Locker Size Confirmed'
            message = f'The locker size has been confirmed. The reservation code is {reservation.code}. \n When loading the package in the locker please enter the correct infromation in the following link: https://tsqrmn8j-8000.brs.devtunnels.ms/operator/ \n \n SACC Team'
            from_email = 'notification@miuandes.cl'
            recipient_list = [reservation.operator.mail]
            send_mail(subject, message, from_email, recipient_list)
            print(f'Email sent to operator ({reservation.operator.mail})')

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
            message = f'Your package is ready to be retrieved. \n Your code is: {reservation.code} \n The locker is located in the following station: {reservation.station} \n Its locker number is: {reservation.locker} \n.Please enter your code and email in the following link to open the locker: https://tsqrmn8j-8000.brs.devtunnels.ms/client/ \n\n SACC Team'
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
            message = 'The package has been retrieved by the client. \n\n SACC Team'
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

                                       
                                    
from .forms import ReservationForm, UserRegisterForm, ConfirmationForm

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

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def reservation_detail(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    cancel_info = CancelReservation.objects.filter(reservation=reservation).first()
    confirmed_info = Confirmed.objects.filter(reservation=reservation).first()
    loaded_info = Loaded.objects.filter(reservation=reservation).first()
    retrieved_info = Retrieved.objects.filter(reservation=reservation).first()

    context = {
        'reservation': reservation,
        'cancel_info': cancel_info,
        'confirmed_info': confirmed_info,
        'loaded_info': loaded_info,
        'retrieved_info': retrieved_info,
    }
    return render(request, 'reservation_detail.html', context)

def dashboard(request):
    # Obtener información actual e histórica de las estaciones
    stations = Station.objects.annotate(
        total_reservations=Count('locker__reservation'),
        avg_time_to_load=Avg(F('locker__reservation__loaded__load_date') - F('locker__reservation__reservation_date')),
        avg_time_to_retrieve=Avg(F('locker__reservation__retrieved__retrieved_date') - F('locker__reservation__loaded__load_date')),
        pending_reservations=Count('locker__reservation__active', filter=Q(locker__reservation__active=True) & Q(locker__reservation__loaded__isnull=True)),
        overdue_packages=Count('locker__reservation__active', filter=Q(locker__reservation__active=True) & Q(locker__reservation__retrieved__isnull=True) & Q(locker__reservation__loaded__isnull=False) & Q(locker__reservation__loaded__load_date__lt=timezone.now() - timezone.timedelta(days=7)))
        
    )
    for station in stations:
        station_reservations= station.reservation_set.all()
        for reservation in station_reservations:
            reservation.cancel_info = CancelReservation.objects.filter(reservation=reservation).first()
            reservation.confirmed_info = Confirmed.objects.filter(reservation=reservation).first()
            reservation.loaded_info = Loaded.objects.filter(reservation=reservation).first()
            reservation.retrieved_info = Retrieved.objects.filter(reservation=reservation).first()
        station.reservations = station_reservations
    context = {'stations': stations}
    return render(request, 'dashboard.html', context)

def confirm_locker(request):
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save to database)
            reservation_code = form.cleaned_data['reservation_code']
            
            data = {
                'code': reservation_code,
            }

            response = requests.post('https://tsqrmn8j-8000.brs.devtunnels.ms/api/confirmed/', data=data)

            if response.status_code == 201:
                messages.success(request, f'Success! Size confirmed. Response: {response.json()}')
            else:
                messages.error(request, f'Error! {response.json()}')
            
            return redirect('confirm_locker')
    else:
        form = ConfirmationForm()

    return render(request, 'confirm_locker.html', {'form': form})