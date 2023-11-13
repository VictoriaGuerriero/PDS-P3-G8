# forms.py
from django import forms

class ReservationForm(forms.Form):
    email = forms.EmailField(label='Email')
    reservation_code = forms.CharField(label='Reservation Code')
