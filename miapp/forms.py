from django import forms
from .models import Articulo, Compra, DatosFacturacion, DatosPersonales, Factura, Usuario
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm


from django import forms 
from django.forms import ModelForm

from ckeditor.widgets import CKEditorWidget

class ArticuloForm(forms.ModelForm):
    stock = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
        label='Stock',
        required=False  # Puedes ajustar esto según tus necesidades
    )

    class Meta:
        model = Articulo
        fields = ['nombre', 'precio', 'descripcion','image','image2','image3','image4', 'tipoCategoria', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Articulo'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'descripcion': CKEditorWidget(attrs={'placeholder': 'Descripcion'}),
            'tipoCategoria': forms.Select(attrs={'class': 'form-control', 'placeholder': 'categoria'}),
        }
        labels = {
            'nombre': "",
            'precio': "",
            'descripcion': "",
            'image': "",
            'image2': "",
            'image3': "",
            'image4': "",
        }
class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
                'username',
                'first_name',
                'last_name',
                'email',
            ]
        
        
        labels = {
                'username':'Nombre de Usuario',
                'first_name': 'Nombre',
                'last_name': 'Apellido',
                'email': 'Correo',
        }

class DatosPersonalesForm(forms.ModelForm):
    CLASE_CHOICES = [
        ("Consumidor Final", "Consumidor Final"),
        ("Monotributo", "Monotributo"),
        ("Responsable Inscripto", "Responsable Inscripto"),
        ("Excento", "Excento")
    ]

    claseFiscalTipo = forms.ChoiceField(
        choices=CLASE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})  # Esto aplicará una clase CSS para el estilo
    )

    class Meta:
        model = DatosPersonales
        fields = ['telefono', 'numeroDocumento', 'claseFiscalTipo']

        labels = {
            'telefono': 'Nro de Teléfono',
            'numeroDocumento': 'Nro de Documento',
            'claseFiscalTipo': 'Tipo de Clase Fiscal',
        }
        

from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)        


class DatosFacturacionForm(forms.ModelForm):
    class Meta:
        model = DatosFacturacion
        fields = ['calle', 'altura', 'piso', 'departamento', 'codigoPostal', 'localidad']
        labels = {
            'calle': 'Calle',
            'altura': 'Altura',
            'piso': 'Piso',
            'departamento': 'Departamento',
            'codigoPostal': 'Código Postal',
            'localidad': 'Localidad',
        }

class CambiarClaveForm(forms.Form):
    nueva_clave = forms.CharField(widget=forms.PasswordInput, label="Nueva Contraseña")
    confirmar_clave = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña anterior",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("La contraseña anterior no es correcta.")
        return old_password    
    



from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['monto', 'monto_total', 'usuario', 'articulos']
        def __init__(self, *args, **kwargs):
            super(CompraForm, self).__init__(*args, **kwargs)
            self.fields['articulos'].widget = forms.SelectMultiple(attrs={'class': 'form-control'})
            self.fields['monto'].required = True
    # def __init__(self, *args, **kwargs):
    #     super(CompraForm, self).__init__(*args, **kwargs)
    #     self.fields['articulos'].widget = forms.SelectMultiple(attrs={'class': 'form-control'})
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['monto'].required = True
        

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['id', 'datosFacturacion', 'compra']

    datosFacturacion = forms.ModelChoiceField(
        queryset=DatosFacturacion.objects.all(),
        label='Datos de Facturación',
        to_field_name='idDatosFacturacion',  # Cambiado a to_field_name
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['datosFacturacion'].queryset = DatosFacturacion.objects.all()
