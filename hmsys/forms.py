# forms.py
from django import forms
from .models import *

class RoomForm(forms.ModelForm):
    class Meta:
        model = Rooms
        fields = ['category', 'number', 'lan_line', 'properties', 'amount', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'lan_line': forms.TextInput(attrs={'class': 'form-control'}),
            'properties': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'occupied': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Service_Request
        fields = ['booked', 'service', 'requested']

class ServicesForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = "__all__"

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payments
        fields = ['client', 'amount_paid', 'mode']

    client = forms.ModelChoiceField(queryset=Client.objects.all())
    amount_paid = forms.IntegerField()
    mode = forms.CharField(max_length=150)