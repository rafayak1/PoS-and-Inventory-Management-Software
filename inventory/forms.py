from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import *
from django import forms

class StockForm(ModelForm):
    class Meta:
        model = stock
        fields = '__all__'

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class PaymentMethodForm(ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method']
        
class Password_Change_Form(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
