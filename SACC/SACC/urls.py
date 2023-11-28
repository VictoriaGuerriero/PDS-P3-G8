"""
URL configuration for SACC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

from LockerBridge.views import (
    ReservationViewSet, ClientViewSet, OperatorViewSet,
    ConfirmedViewSet, LoadedViewSet, RetrievedViewSet, home, operator_view, client_view, register, reservation_detail, dashboard, stations_and_lockers
)
from django.views.generic import RedirectView
from Lockers.views import LockerViewSet, StationViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'reservations', ReservationViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'operators', OperatorViewSet)
router.register(r'confirmeds', ConfirmedViewSet)
router.register(r'loadeds', LoadedViewSet)
router.register(r'retrieveds', RetrievedViewSet)
router.register(r'lockers', LockerViewSet)
router.register(r'stations', StationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', RedirectView.as_view(url='/dashboard/', permanent=True), name='home'),
    path('operator/', operator_view, name='operator_view'),
    path('client/', client_view, name='client_view'),
    path('', include(router.urls)),
    path('register/', register, name='register'),

    path('dashboard/', dashboard, name='dashboard'),
    path('stations_info/', stations_and_lockers, name='stations_info'),

    path('api/reservations/verify-operator/', ReservationViewSet.as_view({'post': 'verify_operator'}), name='verify-operator'),
    path('api/reservations/verify-client/', ReservationViewSet.as_view({'post': 'verify_client'}), name='verify-client'),

]
