from django.utils import timezone
from django.db.models import Count
import json
from math import ceil
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views import View
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.contrib.auth import get_user_model

from decimal import Decimal, InvalidOperation
from ecommerce import settings
from .forms import CustomPasswordChangeForm  # Importa tu formulario personalizado
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth import authenticate, login

from django.http import HttpResponseNotFound, JsonResponse
from .models import Articulo, ItemCarrito

from django.http import HttpResponseRedirect
from django.urls import reverse
  

from django.contrib.auth.mixins import LoginRequiredMixin  
from .forms import *
from .forms import DatosPersonalesForm

# o lo importo de la siguiente manera comentada
from .forms import ArticuloForm
# Create your views here.

from . models import *


from django.views.defaults import page_not_found



class HomeView(TemplateView):
    template_name = "miapp/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todos los objetos Articulo
        articulos = list(Articulo.objects.all())

        # Crear una lista de chunks (grupos) de 3 elementos
        chunk_size = 3
        chunks = [articulos[i:i + chunk_size] for i in range(0, len(articulos), chunk_size)]

        # Obtener la cantidad de artículos en el carrito para el usuario actual
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
               cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto

        context['compras'] = Compra.objects.all()
        context['usuarios'] = Usuario.objects.all()
        context['datos_personales'] = DatosPersonales.objects.all()
        context['datos_facturacion'] = DatosFacturacion.objects.all()
        context['articulos'] = chunks  # Pasa la lista de chunks a la plantilla
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        # Antes de devolver el contexto
        

        return context
    
class Compras(TemplateView):
    template_name = 'miapp/compras.html'
    
    model = Compra,Usuario
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            # Obtener los usuarios y agregarlos al contexto
            
            context['compras'] = Compra.objects.all()
            context['usuarios'] = Usuario.objects.all()
            return context


class UsuariosList(TemplateView):
    template_name = 'miapp/usuarios.html'
    
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            # Obtener los usuarios y agregarlos al contexto
            context['usuarios'] = Usuario.objects.all()
            return context


class DatosPersonalesList(TemplateView):
    model = DatosPersonales


    
class DatosFacturacionList(TemplateView):
    model = DatosFacturacion

class ArticuloView(TemplateView):
    model = Articulo
    template_name = 'miapp/articulos.html'
    # Importa las vistas y modelos necesarios
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener todos los objetos Articulo
        articulos = list(Articulo.objects.all())

        # Crear una lista de chunks (grupos) de 3 elementos
        chunk_size = 6
        chunks = [articulos[i:i + chunk_size] for i in range(0, len(articulos), chunk_size)]

        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto

        context['compras'] = Compra.objects.all()
        context['usuarios'] = Usuario.objects.all()
        context['datos_personales'] = DatosPersonales.objects.all()
        context['datos_facturacion'] = DatosFacturacion.objects.all()
        context['articulos'] = chunks  # Pasa la lista de chunks a la plantilla

        return context

class ArticuloCreate(CreateView):
   
    model = Articulo
    form_class = ArticuloForm
    success_url = reverse_lazy('home')




class AgregarAlCarritoView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        articulo_id = kwargs.get('articulo_id')
        articulo = get_object_or_404(Articulo, pk=articulo_id)
        usuario = request.user  # Obtener el usuario autenticado

        # Verifica si el artículo ya está en el carrito del usuario
        item, created = ItemCarrito.objects.get_or_create(usuario=usuario, articulo=articulo)

        if not created:
            # Si el artículo ya estaba en el carrito del usuario, aumenta la cantidad en uno
            item.cantidad += 1
            item.save()

        # Redirige al usuario a la página de inicio (cambia 'articulos' a la URL de tu elección)
        return HttpResponseRedirect(reverse('articulos'))



@method_decorator(login_required(login_url='/no_registrado/'), name='dispatch')
class VerCarritoView(View):
    template_name = 'miapp/ver_carrito.html'

    def get(self, request, *args, **kwargs):
        # Obtén el usuario autenticado
        usuario = request.user

        # Verifica si el usuario tiene datos de facturación
        tiene_datos_facturacion = DatosFacturacion.objects.filter(user=usuario).exists()

        if tiene_datos_facturacion:
            # Si tiene datos de facturación, obtén todos los elementos del carrito asociados a este usuario
            carrito = ItemCarrito.objects.filter(usuario=usuario)

            # Calcula el total del carrito
            total_carrito = sum(item.precio_total() for item in carrito)

            # Pasa la cantidad y otros datos al contexto
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=usuario).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

            context = {
                'cantidad_en_carrito': cantidad_en_carrito,
                'carrito': carrito,
                'total_carrito': total_carrito,
            }
        else:
            # Si no tiene datos de facturación, redirige a la página para cargarlos
            return redirect('registroDatosPersonales')

        return render(request, self.template_name, context)


class NoRegistradoView(TemplateView):
    template_name = 'miapp/no_registrado.html'    




class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_valid(self, form):
        # Autenticar al usuario utilizando los datos del formulario
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Iniciar sesión si el usuario existe
            login(self.request, user)
            return super().form_valid(form)
        else:
            # Usuario no encontrado, mostrar mensaje de advertencia
            messages.warning(self.request, "El usuario no existe. ¿Deseas registrarte?")
            return super().form_valid(form)
        

class RegistroUsuario(CreateView):
    model = User 
    template_name = "miapp/registro.html"
    form_class = RegistroForm
    success_url = reverse_lazy('home')  
    
class AumentarCantidadView(View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        item = get_object_or_404(ItemCarrito, id=item_id)

        # Verificar si hay suficiente stock
        if item.articulo.stock >= item.cantidad:
            # Aumentar la cantidad en 1
            item.cantidad += 1
            item.save()

            # Devolver una respuesta JSON con la nueva cantidad
            data = {'cantidad': item.cantidad}
        else:
            # No hay suficiente stock, puedes manejar esto de la manera que prefieras
            data = {'error': 'No hay suficiente stock disponible.'}

        return JsonResponse(data)
    # -----------------------------------------------------------?????????--------------------------

class AumentarCantidadView(View):
     def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            item = ItemCarrito.objects.get(id=item_id)
            item.cantidad += 1
            item.save()
        except ItemCarrito.DoesNotExist:
            pass
        return redirect('ver_carrito')
     

class DisminuirCantidadView(View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            item = ItemCarrito.objects.get(id=item_id)
            if item.cantidad > 0:
                item.cantidad -= 1
                item.save()
        except ItemCarrito.DoesNotExist:
            pass
        return redirect('ver_carrito')
    

class EliminarDelCarritoView(View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            item = ItemCarrito.objects.get(id=item_id)
            item.delete()
        except ItemCarrito.DoesNotExist:
            pass
        return redirect('ver_carrito')    
    


class IrAPagarView(View):
    def get(self, request, *args, **kwargs):
        # Aquí puedes realizar las acciones necesarias antes de redirigir al proceso de pago
        # Por ejemplo, puedes verificar si el carrito está vacío
        usuario = self.request.user
        carrito = ItemCarrito.objects.filter(usuario=usuario)
        
        if not carrito.exists():
            # Si el carrito está vacío, muestra un mensaje al usuario y redirige al carrito
            messages.warning(request, 'Tu carrito está vacío. Agrega productos antes de pagar.')
            return redirect('ver_carrito')

        # Redirige a la página de pago (ajusta la URL según tu aplicación)
        return redirect('registroDatos')
    


class CancelarCompraView(View):
    def get(self, request, *args, **kwargs):
        # Aquí puedes realizar las acciones necesarias para cancelar la compra
        # En este ejemplo, simplemente vaciamos el carrito
        usuario = self.request.user
        carrito = ItemCarrito.objects.filter(usuario=usuario)
        carrito.delete()
        
        # Muestra un mensaje de éxito al usuario y redirige al carrito vacío
        messages.success(request, 'Compra cancelada con éxito. Tu carrito está vacío.')
        return redirect('ver_carrito')
    

# @method_decorator(login_required, name='dispatch')
class RegistroDatosPersonales(LoginRequiredMixin, CreateView):
    model = DatosPersonales
    template_name = "miapp/datosPersonales_form.html"
    form_class = DatosPersonalesForm
    success_url = reverse_lazy('home')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datos_personales_form = DatosPersonalesForm()  # Intenta inicializar el formulario aquí
        print(datos_personales_form.is_bound)  # Verifica si el formulario está enlazado
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['datos_personales_form'] = datos_personales_form
        context['datos_facturacion_form'] = DatosFacturacionForm()
        return context

    def form_valid(self, form):
    # Guardar datos de DatosPersonales
        print("Usuario actual:", self.request.user)
        print("Datos del formulario de facturación:", self.request.POST)

        datos_personales = form.save(commit=False)
        datos_personales.user = self.request.user  # Asignar usuario actual
        datos_personales.save()

        # Guardar datos de DatosFacturacion
        datos_facturacion_form = DatosFacturacionForm(self.request.POST)
        if datos_facturacion_form.is_valid():
            datos_facturacion = datos_facturacion_form.save(commit=False)
            datos_facturacion.user = self.request.user  # Asignar usuario actual
            datos_facturacion.save()

        return super().form_valid(form)
    
class ArticuloDetailView(DetailView):
    model = Articulo
    template_name = "miapp/articulo_detail.html"

    # Puedes agregar más contexto si es necesario
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí puedes agregar más contexto si lo necesitas
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        return context
    


class SearchView(View):#es del base de ventas
    template_name = 'miapp/articulos.html'

    def get(self, request, *args, **kwargs):
        nombre = self.request.GET.get("nombre")
        articulos = Articulo.objects.filter(nombre__icontains=nombre) if nombre else Articulo.objects.all()
        chunk_size = 3  # Tamaño de cada "chunk"
        chunks = [articulos[i:i + chunk_size] for i in range(0, len(articulos), chunk_size)]

        context = {'articulos': chunks}
        return render(request, self.template_name, context)

class ArticuloUpdate(LoginRequiredMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name_suffix = "_update_form"
    
    def get_success_url(self):
        return reverse_lazy('articulo-update', args=[self.object.id])+'?ok'    
    
class MovieDelete(LoginRequiredMixin, DeleteView):
    model = Articulo
    success_url = reverse_lazy('articulos')  



class CrearDatosFacturacionView(LoginRequiredMixin, View):
    template_name = 'miapp/datosFacturacion.html'

    def get(self, request):
        form = DatosFacturacionForm()
        # Obtener el carrito del usuario autenticado
        carrito = ItemCarrito.objects.filter(usuario=request.user)
        # Calcular el total del carrito
        total_carrito = sum(item.precio_total() for item in carrito)
        return render(request, self.template_name, {'form': form, 'carrito': carrito, 'total_carrito': total_carrito})

    def post(self, request):
        form = DatosFacturacionForm(request.POST)
        if form.is_valid():
            datos_facturacion = form.save()
            # Puedes hacer algo después de guardar los datos de facturación aquí
            return redirect('ver_carrito')  # Reemplaza 'alguna_vista' con tu URL deseada

        # Obtener el carrito del usuario autenticado
        carrito = ItemCarrito.objects.filter(usuario=request.user)
        # Calcular el total del carrito
        total_carrito = sum(item.precio_total() for item in carrito)
        return render(request, self.template_name, {'form': form, 'carrito': carrito, 'total_carrito': total_carrito})

from django.contrib.auth import get_user_model, login
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import check_password
from .forms import CambiarClaveForm
from .models import ItemCarrito
from django.db.models import Sum

class CambiarClaveView(View):
    def get(self, request, *args, **kwargs):
        form = CambiarClaveForm(user=request.user)  # Pasa el usuario al formulario
        return render(request, 'miapp/cambiar_clave.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CambiarClaveForm(request.POST, user=request.user)  # También pasa el usuario en el POST
        if form.is_valid():
            # Lógica para cambiar la contraseña
            nueva_clave = form.cleaned_data['nueva_clave']
            usuario = request.user
            usuario.set_password(nueva_clave)
            usuario.save()  # Guarda el nuevo valor de la contraseña
            return redirect('home')  # Redirige después de cambiar la contraseña
        return render(request, 'miapp/cambiar_clave.html', {'form': form})
    

    
from miapp.models import ItemCarrito  

import mercadopago
from django.conf import settings
from django.shortcuts import render
from django.views import View
from .models import ItemCarrito

from django.shortcuts import render
from django.conf import settings
from django.views import View
import mercadopago
from .models import ItemCarrito



# #este es el oficial de mercado pago
# class IniciarPagoView(View):
#     template_name = 'miapp/iniciar_pago.html'

#     def get(self, request):
#         # Configuración de Mercado Pago
#         mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

#         # Obtén los artículos del carrito
#         if request.user.is_authenticated:
#             carrito = ItemCarrito.objects.filter(usuario=request.user)
#         else:
#             carrito = []

#         # Calcula el total del carrito
#         total_carrito = sum(float(item.precio_total()) if callable(item.precio_total) else float(item.precio_total) for item in carrito)

#         # Datos del comprador
#         if request.user.is_authenticated:
#             comprador_email = request.user.email  # Usamos el email del usuario autenticado
#         else:
#             comprador_email = "comprador_default@dominio.com"  # Correo de prueba si no está autenticado

#         # Datos del vendedor (puedes ajustarlo según lo que necesites)
#         vendedor_email = "vendedor@dominio.com"  # Correo del vendedor (ejemplo)

#         # Crea la preferencia de pago
#         preference_data = {
#             "items": [
#                 {
#                     "title": "Compra de productos",
#                     "quantity": 1,
#                     "currency_id": "ARS",  # Moneda en pesos argentinos
#                     "unit_price": total_carrito  # Usa el total_carrito como precio unitario
#                 }
#             ],
#             "payer": {
#                 "email": comprador_email  # Correo del comprador
#             },
#             "back_urls": {
#                 "success": "http://127.0.0.1:8000/",  # Redirigir a la URL de éxito
#                 "failure": "http://www.tusitio.com/failure",  # Redirigir a la URL de fracaso
#                 "pending": "http://www.tusitio.com/pending",   # Redirigir a la URL de pendiente
#             },
#             "auto_return": "approved",
#             "notification_url": "http://www.tusitio.com/notification",  # URL para recibir notificaciones
#             "marketplace": "NONE",  # Definir el tipo de mercado
#             "site_id": "MLA"  # ID de la región (Argentina)
#         }

#         preference = mp.preference().create(preference_data)
#         print(json.dumps(preference, indent=4))  # Imprime la respuesta de la API completa

#         # Verifica si la clave 'id' está presente
#         if 'id' in preference['response']:
#             preference_id = preference['response']['id']
#         else:
#             print("Error: 'id' no encontrado en la respuesta")


#         # Pasa los datos necesarios a la plantilla
#         context = {
#             'public_key': settings.MERCADOPAGO_PUBLIC_KEY,  # Clave pública
#             'preference_id': preference_id,                # ID de la preferencia
#             'total_carrito': total_carrito,                 # Total del carrito
#         }

#         return render(request, self.template_name, context)


from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.views import View
import mercadopago
import json
from decimal import Decimal

from django.views import View
from django.shortcuts import render
import mercadopago
from django.conf import settings
from miapp.models import ItemCarrito


class IniciarPagoView(View):
    template_name = 'miapp/iniciar_pago.html'

    def get(self, request):
        print("Inicio del método GET")

        # Configuración de Mercado Pago
        mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        print("Configuración de Mercado Pago completada")

        # Obtén los artículos del carrito
        if request.user.is_authenticated:
            carrito = ItemCarrito.objects.filter(usuario=request.user)
            print("Carrito obtenido para el usuario autenticado")
        else:
            carrito = []
            print("Carrito vacío para usuario no autenticado")

        # Si el carrito está vacío, no se puede realizar la compra
        if not carrito:
            print("El carrito está vacío")
            return render(request, 'miapp/error.html', {'error_message': "El carrito está vacío"})

        # Calcula el total del carrito
        total_carrito = sum(float(item.precio_total()) if callable(item.precio_total) else float(item.precio_total) for item in carrito)
        print(f"Total del carrito calculado: {total_carrito}")

        # Calcular la cantidad total de productos en el carrito
        cantidad_en_carrito = carrito.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad'] or 0

        # Datos del comprador
        if request.user.is_authenticated:
            comprador_email = request.user.email  # Usamos el email del usuario autenticado
            print(f"Email del comprador: {comprador_email}")
        else:
            comprador_email = "comprador_default@dominio.com"  # Correo de prueba si no está autenticado
            print("Email del comprador por defecto")

        # Crea la preferencia de pago
        preference_data = {
            "items": [
                {
                    "title": "Compra de productos",
                    "quantity": 1,
                    "currency_id": "ARS",  # Moneda en pesos argentinos
                    "unit_price": total_carrito  # Usa el total_carrito como precio unitario
                }
            ],
            "payer": {
                "email": comprador_email  # Correo del comprador
            },
            "back_urls": {
                "success": "http://127.0.0.1:8000/success",  # Redirigir a la URL de éxito
                "failure": "http://127.0.0.1:8000/failure",  # Redirigir a la URL de fracaso
                "pending": "http://127.0.0.1:8000/pending",  # Redirigir a la URL de pendiente
            },
            "auto_return": "approved",
            "notification_url": "http://www.tusitio.com/notification",  # URL para recibir notificaciones
            "marketplace": "NONE",  # Definir el tipo de mercado
            "site_id": "MLA"  # ID de la región (Argentina)
        }

        preference = mp.preference().create(preference_data)
        print("Preferencia de pago creada")

        # Verifica si la clave 'id' está presente
        if 'id' in preference['response']:
            preference_id = preference['response']['id']
            print(f"ID de preferencia obtenido: {preference_id}")
        else:
            print("Error: 'id' no encontrado en la respuesta")
            return render(request, 'miapp/error.html', {'error_message': "No se pudo obtener el ID de la preferencia."})

        # Pasa los datos necesarios a la plantilla
        context = {
            'public_key': settings.MERCADOPAGO_PUBLIC_KEY,  # Clave pública
            'preference_id': preference_id,                 # ID de la preferencia
            'total_carrito': total_carrito, 
            'total_carrito': total_carrito,                                 # Total del carrito
            'cantidad_en_carrito': cantidad_en_carrito      # Agregar la cantidad total del carrito
        }
        print("Datos pasados al contexto de la plantilla")
        return render(request, self.template_name,  context)

    
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SuccessView(View):
    template_name = 'miapp/success.html'

    @transaction.atomic
    def get(self, request):
        if request.user.is_authenticated:
            usuario = request.user
            carrito = ItemCarrito.objects.filter(usuario=usuario)

            if not carrito:
                return render(request, 'miapp/error.html', {'error_message': "El carrito está vacío."})

            total_carrito = sum(float(item.precio_total()) if callable(item.precio_total) else float(item.precio_total) for item in carrito)

            try:
                # Crear la compra utilizando el usuario autenticado
                compra = Compra.objects.create(monto=total_carrito, monto_total=total_carrito, usuario=usuario)

                # Crear registros de ArticuloCompra para cada item del carrito
                for item_carrito in carrito:
                    ArticuloCompra.objects.create(compra=compra, articulo=item_carrito.articulo, cantidad=item_carrito.cantidad)

                # Obtener los datos de facturación del usuario
                datos_facturacion = DatosFacturacion.objects.filter(user=compra.usuario).first()

                # Crear y guardar la factura con la relación
                if datos_facturacion:
                    factura_form = FacturaForm({'datosFacturacion': datos_facturacion.idDatosFacturacion, 'compra': compra.idCompra})
                    if factura_form.is_valid():
                        factura_form.save()

                # Actualizar el stock de los artículos
                for item_carrito in carrito:
                    articulo = item_carrito.articulo
                    articulo.stock -= item_carrito.cantidad
                    articulo.save()

                # Eliminar los items del carrito después de la compra
                carrito.delete()

                articulos = ArticuloCompra.objects.filter(compra=compra)
                return render(request, self.template_name, {
                    'message': 'Compra realizada con éxito.',
                    'compra': compra,
                    'articulos': articulos
                })

            except Exception as e:
                print(f"Error: {str(e)}")
                transaction.set_rollback(True)
                return render(request, 'miapp/error.html', {'error_message': "Error al procesar la compra."})

        else:
            return render(request, 'miapp/error.html', {'error_message': "Usuario no autenticado"})

class FailureView(View):
    def get(self, request):
        return render(request, 'miapp/error.html', {'error_message': "El pago ha fallado. Por favor, intenta nuevamente."})

class PendingView(View):
    def get(self, request):
        return render(request, 'miapp/pending.html', {'message': "Tu pago está pendiente. Te notificaremos una vez que se confirme."})
# # Integración con PayPal (nuevo código)
# import paypalrestsdk




#------ESTE ES EL OFICIAL de PAYPAL----------------
from django.conf import settings


from django.db import transaction

@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class ConfirmacionPago(View):
    template_name = 'miapp/confirmacion.html'

    @transaction.atomic
    def post(self, request):
        total_carrito_str = request.POST.get('total_carrito')
        print(request.POST)
        print("Total del carrito recibido:", total_carrito_str)

        # Obtener el usuario autenticado
        usuario = request.user

        # Obtener los items del carrito del usuario
        items_carrito = ItemCarrito.objects.filter(usuario=usuario)

        # Verificar si hay artículos en el carrito
        if not items_carrito.exists():
            # Redirigir a la página de error si no hay artículos
            return render(request, 'miapp/error.html')

        if total_carrito_str is not None:
            total_carrito_str = total_carrito_str.replace(',', '.')
            total_carrito_str = ''.join(c for c in total_carrito_str if c.isdigit() or c == '.')

            # Verificar si total_carrito_str es un número válido
            if total_carrito_str.replace('.', '').isdigit():
                # Convertir a Decimal
                total_carrito = Decimal(total_carrito_str)

                # Crear la compra utilizando el usuario autenticado
                with transaction.atomic():
                    compra = Compra.objects.create(monto=total_carrito, monto_total=total_carrito, usuario=usuario)

                    # Crear registros de ArticuloCompra para cada item del carrito
                    for item_carrito in items_carrito:
                        ArticuloCompra.objects.create(compra=compra, articulo=item_carrito.articulo, cantidad=item_carrito.cantidad)
                    # Obtener los datos de facturación del usuario
                    # Obtener los datos de facturación del usuario
                    datos_facturacion = DatosFacturacion.objects.filter(user=compra.usuario).first()

                    # # Crear y guardar la factura con la relación
                    factura_form = FacturaForm({'datosFacturacion': datos_facturacion.idDatosFacturacion, 'compra': compra.idCompra})
                    if factura_form.is_valid():
                        factura = factura_form.save()
                    # Actualizar el stock de los artículos
                    for item_carrito in items_carrito:
                        articulo = item_carrito.articulo
                        cantidad_vendida = item_carrito.cantidad
                        articulo.stock -= cantidad_vendida
                        articulo.save()

                    # Eliminar los items del carrito después de la compra
                    items_carrito.delete()

                    # Realizar otras operaciones relacionadas con la compra según sea necesario

                    # Renderizar la página de confirmación con los datos necesarios
                    context = {'compra': compra}
                    return render(request, self.template_name, context)
            else:
                print("Error: total_carrito_str no es un número válido")
                # Manejar el error de alguna manera, por ejemplo, redirigir a una página de error
                return render(request, 'miapp/error.html')
        else:
            print("Error: total_carrito_str es None")
            # Manejar el error de alguna manera, por ejemplo, redirigir a una página de error
            return render(request, 'miapp/error.html')
        
#------FIN DEL OFICIAL----------------





import mercadopago
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from miapp.models import ItemCarrito, Compra, ArticuloCompra, DatosFacturacion
from miapp.forms import FacturaForm

@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class ConfirmacionPago(View):
    template_name = 'miapp/confirmacion.html'

    @transaction.atomic
    def post(self, request):
        total_carrito_str = request.POST.get('total_carrito')
        print(request.POST)
        print("Total del carrito recibido:", total_carrito_str)

        # Obtener el usuario autenticado
        usuario = request.user

        # Obtener los items del carrito del usuario
        items_carrito = ItemCarrito.objects.filter(usuario=usuario)

        # Verificar si hay artículos en el carrito
        if not items_carrito.exists():
            # Redirigir a la página de error si no hay artículos
            return render(request, 'miapp/error.html')

        if total_carrito_str is not None:
            total_carrito_str = total_carrito_str.replace(',', '.')
            total_carrito_str = ''.join(c for c in total_carrito_str if c.isdigit() or c == '.')

            # Verificar si total_carrito_str es un número válido
            if total_carrito_str.replace('.', '').isdigit():
                # Convertir a Decimal
                total_carrito = Decimal(total_carrito_str)

                # Crear la compra utilizando el usuario autenticado
                with transaction.atomic():
                    compra = Compra.objects.create(monto=total_carrito, monto_total=total_carrito, usuario=usuario)

                    # Crear registros de ArticuloCompra para cada item del carrito
                    for item_carrito in items_carrito:
                        ArticuloCompra.objects.create(compra=compra, articulo=item_carrito.articulo, cantidad=item_carrito.cantidad)
                    # Obtener los datos de facturación del usuario
                    # Obtener los datos de facturación del usuario
                    datos_facturacion = DatosFacturacion.objects.filter(user=compra.usuario).first()

                    # # Crear y guardar la factura con la relación
                    factura_form = FacturaForm({'datosFacturacion': datos_facturacion.idDatosFacturacion, 'compra': compra.idCompra})
                    if factura_form.is_valid():
                        factura = factura_form.save()
                    # Actualizar el stock de los artículos
                    for item_carrito in items_carrito:
                        articulo = item_carrito.articulo
                        cantidad_vendida = item_carrito.cantidad
                        articulo.stock -= cantidad_vendida
                        articulo.save()

                    # Eliminar los items del carrito después de la compra
                    items_carrito.delete()

                    # Realizar otras operaciones relacionadas con la compra según sea necesario

                    # Renderizar la página de confirmación con los datos necesarios
                    context = {'compra': compra}
                    return render(request, self.template_name, context)
            else:
                print("Error: total_carrito_str no es un número válido")
                # Manejar el error de alguna manera, por ejemplo, redirigir a una página de error
                return render(request, 'miapp/error.html')
        else:
            print("Error: total_carrito_str es None")
            # Manejar el error de alguna manera, por ejemplo, redirigir a una página de error
            return render(request, 'miapp/error.html')
        





























































# def ver_datos_usuario(request):
#     # Verifica si el usuario está autenticado
#     if request.user.is_authenticated:
#         # Obtiene el objeto User asociado al usuario autenticado
#         usuario = User.objects.get(username=request.user.username)
        
#         # Obtiene el objeto DatosPersonales asociado al usuario
#         datos_personales = DatosPersonales.objects.filter(user=usuario).first()
        
#         # Si no hay datos personales, redirige al usuario a la página de registro o actualización de datos personales
#         if datos_personales is None:
#             return redirect('registroDatosPersonales')
        
#         # Obtiene el objeto DatosFacturacion asociado al usuario
#         datos_facturacion = DatosFacturacion.objects.filter(user=usuario).first()
        
#         # Renderiza la plantilla y pasa los datos_personales, datos_facturacion y usuario
#         return render(request, 'miapp/ver_datos_usuario.html', {
#             'datos_personales': datos_personales,
#             'datos_facturacion': datos_facturacion,
#             'usuario': usuario,
#         })
#     else:
#         # Redirige al usuario a la página de inicio de sesión si no está autenticado
#         return redirect('login')

class VerDatosUsuarioView(TemplateView):
    template_name = 'miapp/ver_datos_usuario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Verifica si el usuario está autenticado
        if self.request.user.is_authenticated:
            # Obtiene el objeto User asociado al usuario autenticado
            usuario = User.objects.get(username=self.request.user.username)
            
            # Obtiene el objeto DatosPersonales asociado al usuario
            datos_personales = DatosPersonales.objects.filter(user=usuario).first()
            
            # Si no hay datos personales, redirige al usuario a la página de registro o actualización de datos personales
            if datos_personales is None:
                return redirect('registroDatosPersonales')

            # Obtiene el objeto DatosFacturacion asociado al usuario
            datos_facturacion = DatosFacturacion.objects.filter(user=usuario).first()
            cantidad_en_carrito = 0
            if self.request.user.is_authenticated:
                cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
            context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
            # Pasa los datos al contexto
            context['datos_personales'] = datos_personales
            context['datos_facturacion'] = datos_facturacion
            context['usuario'] = usuario
        else:
            # Redirige al usuario a la página de inicio de sesión si no está autenticado
            return redirect('login')

        return context


class DatosPersonalesUpdate(LoginRequiredMixin, UpdateView):
    model = DatosPersonales
    form_class = DatosPersonalesForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        # Redirige a la misma página con el mensaje de éxito
        return reverse_lazy('datospersonales-update', kwargs={'pk': self.object.pk}) + '?ok'

    def form_valid(self, form):
        # Guarda los datos del formulario en el modelo `DatosPersonales`
        response = super().form_valid(form)

        # Actualiza los datos del usuario asociado
        user = self.object.user  # Relación OneToOneField con User
        user.first_name = form.cleaned_data.get('nombre')  # Asegúrate de que el campo 'nombre' está en el formulario
        user.last_name = form.cleaned_data.get('apellido')
        user.email = form.cleaned_data.get('correo')
        user.save()  # Faltaba llamar al método save()

        return response

    def get_context_data(self, **kwargs):
        # Agrega el usuario al contexto de la plantilla
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context
    


class DatosFactuacionUpdate(LoginRequiredMixin, UpdateView):
    model = DatosFacturacion
    form_class = DatosFacturacionForm
    template_name_suffix = "_update_form"
    
    def get_success_url(self):
        return reverse_lazy('datosfacturacion-update', kwargs={'pk': self.object.pk}) + '?ok'    
    


class ArticuloDelete(LoginRequiredMixin, DeleteView):
    model = Articulo
    success_url = reverse_lazy('articulos')    


class BaseView(TemplateView):
    template_name = 'miapp/base.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los artículos de cada compra
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto





class CompraListView(ListView):
    model = Compra
    template_name = 'miapp/compras.html'
    context_object_name = 'compras'
    paginate_by = 10  # Número de compras por página

    def get_queryset(self):
        # Ordena las compras por fecha en orden descendente
        return Compra.objects.order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los artículos de cada compra
        compras_con_articulos = []
        for compra in context['compras']:
            articulos = compra.articulos.all()
            compras_con_articulos.append({'compra': compra, 'articulos': articulos})
        context['compras_con_articulos'] = compras_con_articulos

        # Agrega el formulario de CompraForm al contexto
        context['form'] = CompraForm()

        return context

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')
        if action == 'edit':
            # Obtener el ID de la compra desde los parámetros de la URL
            pk = request.GET.get('pk')
            compra = get_object_or_404(Compra, idCompra=pk)
            form = CompraForm(instance=compra)  # Cargar el formulario con la instancia de la compra
            # Puedes enviar el formulario al contexto si lo necesitas en tu template
            return render(request, 'compras.html', {'form': form, 'compra': compra, 'monto_actual': compra.monto})
        else:
            return super().get(request, *args, **kwargs)


    





class CompraUpdate(LoginRequiredMixin, UpdateView):
    model = Compra
    form_class = CompraForm
    template_name_suffix = "_update_form"
    
    def get_success_url(self):
        return reverse_lazy('compra-update', kwargs={'pk': self.object.pk}) + '?ok'    
    

class CompraDelete(LoginRequiredMixin, DeleteView):
    model = Compra
    success_url = reverse_lazy('compras') 

from django.http import JsonResponse
from django.template.loader import render_to_string

def load_modal_content(request):
    # Cargar el contenido del modal desde el template
    modal_content = render_to_string('compras_update_form.html')
    return JsonResponse({'modal_content': modal_content})





# class CompraDelete(LoginRequiredMixin, DeleteView):
#     model = Compra
#     template_name = 'miapp/compras.html'
#     success_url = reverse_lazy('compras') 
#     def get_object(self, queryset=None):
#         pk = self.kwargs.get('pk')
#         return get_object_or_404(self.model, pk=pk)
#     def get_success_url(self):
#         return reverse_lazy('compra-delete', kwargs={'pk': self.object.pk}) + '?ok'   

# def mostrar_usuarios(request):
#     # Obtiene todos los usuarios de la base de datos
#     usuarios = User.objects.all()

#     # Pasa los usuarios al template
#     contexto = {
#         'usuarios': usuarios
#     }

#     # Renderiza el template y pasa el contexto
#     return render(request, 'miapp/listausuarios.html', contexto)
class MostrarUsuariosView(TemplateView):
    template_name = 'miapp/listadousuarios.html'  # Nombre del template

    def get_context_data(self, **kwargs):
        # Obtiene todos los usuarios de la base de datos
        usuarios = User.objects.all()
        # Crea el contexto con los usuarios
        context = super().get_context_data(**kwargs)
        context['usuarios'] = usuarios
        return context

# views.py
def guardar_usuario(request, usuario_id):
    if request.method == 'POST':
        # Obtén el objeto User correspondiente al usuario_id
        usuario = get_object_or_404(User, pk=usuario_id)

        # Obtén los datos del cuerpo de la solicitud
        data = json.loads(request.body)

        # Actualiza los campos del objeto User con los datos proporcionados
        usuario.first_name = data.get('first_name')
        usuario.last_name = data.get('last_name')
        usuario.email = data.get('email')

        # Guarda los cambios en la base de datos
        usuario.save()

        return JsonResponse({'mensaje': 'Datos actualizados correctamente'})
    return JsonResponse({'error': 'Método no permitido'})


class VistaAdmin(ListView):
    model = Compra  # Especifica el modelo a utilizar en la vista
    template_name = 'miapp/vista_admin.html'  # Especifica el nombre del template a utilizar
    context_object_name = 'compras'  # Especifica el nombre de la variable de contexto en el template (opcional)

    # Opcional: Puedes agregar más contexto si es necesario
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agrega más contexto si es necesario
        return context
class VistaBase(ListView):
    model = Compra  # Especifica el modelo a utilizar en la vista
    template_name = 'miapp/base1.html'  # Especifica el nombre del template a utilizar


class VistaDetalle(DetailView):
    model = Articulo
    template_name = 'miapp/detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['pk']  # Obtén el ID del artículo desde los parámetros de la URL
        articulo = Articulo.objects.get(id=id)  # Obtén el artículo por su ID
        context['object'] = articulo
        return context


class AccesoriosListView(TemplateView):
    Model = Articulo
    template_name = 'miapp/accesorios.html'  # Reemplaza 'ruta_de_tu_template.html' con la ruta correcta de tu template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtrar los artículos por la categoría "Accesorios"
        accesorios = Articulo.objects.filter(tipoCategoria='Accesorios')
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['accesorios'] = accesorios
        return context
    

class ComponentesListView(TemplateView):
    Model = Articulo
    template_name = 'miapp/componentes.html'  # Reemplaza 'ruta_de_tu_template.html' con la ruta correcta de tu template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtrar los artículos por la categoría "Accesorios"
        accesorios = Articulo.objects.filter(tipoCategoria='Componentes')
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['componentes'] = accesorios
        return context    
    

class ComputacionListView(TemplateView):
    Model = Articulo
    template_name = 'miapp/computacion.html'  # Reemplaza 'ruta_de_tu_template.html' con la ruta correcta de tu template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtrar los artículos por la categoría "Accesorios"
        accesorios = Articulo.objects.filter(tipoCategoria='Computacion')
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['computacion'] = accesorios
        return context        
    
class VerComprasView(LoginRequiredMixin, TemplateView):
    template_name = 'miapp/ver_compras.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar el objeto de usuario al contexto
        context['usuario'] = self.request.user
        
        # Obtén todas las compras del usuario actual, ordenadas por fecha de manera descendente
        compras = Compra.objects.filter(usuario=self.request.user).order_by('-fecha')
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['compras'] = compras
        return context
    

class VistaCompraConfirmada(LoginRequiredMixin, View):
    template_name = 'miapp/compraConfirmada.html'
    error_template_name = 'miapp/error2.html'

    def get(self, request, *args, **kwargs):
        # Obtener el ID de la compra de los parámetros de la URL
        compra_id = kwargs.get('compra_id')

        if compra_id:
            try:
                # Obtener la compra correspondiente
                compra = Compra.objects.get(pk=compra_id)

                # Agregar la compra al contexto
                context = {'compra': compra}

                # Renderizar la página de confirmación con los datos necesarios
                return render(request, self.template_name, context)
            except Compra.DoesNotExist:
                # Manejar el caso en el que la compra no existe
                return render(request, self.error_template_name)
        else:
            # Manejar el caso en el que no se proporcionó el ID de la compra
            return render(request, self.error_template_name)
        

class VerCompraDetail(DetailView):
    model = Compra
    template_name = "miapp/compra_detail.html"

    # Puedes agregar más contexto si es necesario
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cantidad_en_carrito = 0
        compra = get_object_or_404(Compra, pk=self.kwargs['pk'])
        articulos_compra = ArticuloCompra.objects.filter(compra=compra)

        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito 
        context['articulos_compra'] = articulos_compra # Pasa la cantidad al contexto
        # Aquí puedes agregar más contexto si lo necesitas
        return context



from decimal import Decimal

class FacturaView(TemplateView):
    model = Compra
    template_name = 'miapp/factura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtén la compra
        compra = get_object_or_404(Compra, pk=self.kwargs['pk'])
        # Obtén los artículos asociados a la compra
        articulos_compra = ArticuloCompra.objects.filter(compra=compra)

        # Calcular el subtotal y el 21% para cada artículo
        for articulo in articulos_compra:
            cantidad_decimal = Decimal(articulo.cantidad)
            precio_decimal = Decimal(articulo.articulo.precio)
            
            # Calcular el precio por unidad
            articulo.precio_por_unidad = precio_decimal

            # Calcular el subtotal
            articulo.subtotal = cantidad_decimal * precio_decimal
            articulo.iva = articulo.subtotal * Decimal('0.21')

            # Calcular el subtotal sin IVA
            articulo.subtotal_sin_iva = articulo.subtotal - articulo.iva

            # Calcular el subtotal después de aplicar el IVA
            articulo.subtotal_con_iva = articulo.subtotal + articulo.iva
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
            cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto

        # Agregar los datos al contexto
        context['compra'] = compra
        context['articulos_compra'] = articulos_compra

        # Agregar el usuario asociado a la compra
        context['usuario'] = compra.usuario

        # Obtener los datos de facturación del usuario
        datos_facturacion = DatosFacturacion.objects.filter(user=compra.usuario).first()
        context['datos_facturacion'] = datos_facturacion

        # Obtener los datos personales del usuario
        datos_personales = DatosPersonales.objects.filter(user=compra.usuario).first()
        context['datos_personales'] = datos_personales

        # Agregar la fecha actual al contexto
        context['fecha_actual'] = timezone.now()

        return context

class CompraConfirmadaView(TemplateView):    
    Model = Compra
    template_name = 'miapp/confirmacionCompra.html'



class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'miapp/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el usuario autenticado
        usuario = self.request.user

        # Obtener las compras asociadas al usuario
        compras = Compra.objects.filter(usuario=usuario)

        # Obtén todas las compras del usuario actual, ordenadas por fecha de manera descendente
        compras = Compra.objects.filter(usuario=self.request.user).order_by('-fecha')

        # Obtener los datos personales del usuario
        datos_personales = DatosPersonales.objects.filter(user=usuario).first()

        # Obtener la cantidad total de compras del usuario
        total_compras = compras.aggregate(total_compras=Sum('articulocompra__cantidad'))['total_compras']
        cantidad_en_carrito = 0
        if self.request.user.is_authenticated:
               cantidad_en_carrito = ItemCarrito.objects.filter(usuario=self.request.user).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        context['cantidad_en_carrito'] = cantidad_en_carrito  # Pasa la cantidad al contexto
        context['datos_personales'] = datos_personales
        context['compras'] = compras
        context['total_compras'] = total_compras

        
        return context
    

from django.contrib.auth.models import User

class ControlStockView(View):
    template_name = 'miapp/control_stock.html'

    def get(self, request, *args, **kwargs):
        # Obtener todos los artículos
        articulos = Articulo.objects.all()

        # Obtener la cantidad de compras por usuario
        compras_por_usuario = User.objects.annotate(total_compras=Count('compra'))
        articulo_mas_comprado = Compra.objects.values('articulos__nombre').annotate(total_compras=Count('articulos__nombre'))


        # Pasa los artículos y la información de las compras al contexto
        context = {'articulos': articulos, 'compras_por_usuario': compras_por_usuario, 'articulo_mas_comprado': articulo_mas_comprado}
        return render(request, self.template_name, context)


class FacturaNuevaView(View):
    template_name = 'miapp/nuevaFactura.html'

    def get(self, request):
        form = FacturaForm()

        # Obtén las compras con facturas asociadas del usuario actual
        usuario = request.user
        compras = Compra.objects.filter(usuario=usuario, factura__isnull=False)

        # Pasa las compras al contexto de la plantilla
        return render(request, self.template_name, {'form': form, 'compra': compras.first()})

    def post(self, request):
        form = FacturaForm(request.POST)
        if form.is_valid():
            datos_facturacion_id = form.cleaned_data['datos_facturacion_id']
            compra_id = form.cleaned_data['compra_id']

            # Crea una instancia de Factura y guárdala en la base de datos
            factura = Factura(datosFacturacion_id=datos_facturacion_id, compra_id=compra_id)
            factura.save()

            # Aquí puedes redirigir a una página de éxito o hacer cualquier otra acción necesaria
            return render(request, 'success_template.html')  # Reemplaza 'success_template.html' con el nombre de tu plantilla de éxito

        return render(request, self.template_name, {'form': form})