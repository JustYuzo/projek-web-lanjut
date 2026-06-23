from django import forms
from .models import Car


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['name', 'brand', 'transmission', 'capacity', 'price', 'image']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Contoh: Avanza Veloz'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Contoh: Toyota'
            }),
            'transmission': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Contoh: Manual / Matic / Automatic'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Contoh: 7'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Contoh: 450000'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input'
            }),
        }