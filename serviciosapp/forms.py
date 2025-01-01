from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Cliente

class ClienteForm(forms.ModelForm):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
        label='Nombre',
        required=False  # Puedes ajustar esto según tus necesidades
    )

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo and '@' not in correo:  # Verifica si el correo contiene '@'
            raise ValidationError(_('Correo electrónico no válido. Debe contener un "@".'), code='invalid')
        return correo

    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'correo']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'}),
            'correo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo'}),
        }
