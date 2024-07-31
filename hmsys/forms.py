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
