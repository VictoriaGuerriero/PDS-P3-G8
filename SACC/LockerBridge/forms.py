# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ReservationForm(forms.Form):
    email = forms.EmailField(label='Email')
    reservation_code = forms.CharField(label='Reservation Code')

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label='Username',
        help_text='')
    email = forms.EmailField(
        label='Email',
        help_text=''
    )
    password1 = forms.CharField(
        label='Password',
        help_text='')
    password2 = forms.CharField(
        label='Confirm Password',
        help_text=''
    )
    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1','password2']

class ConfirmationForm(forms.Form):
    reservation_code = forms.CharField(label='Reservation Code', max_length=200)