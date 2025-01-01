from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,TemplateView
from .models import Cliente
from .forms import ClienteForm
from miapp.models import Articulo,ItemCarrito,Compra,DatosPersonales,DatosFacturacion,Usuario
from django.db.models import Sum

# Create your views here.



class ClienteListView(ListView):
    model = Cliente
    template_name = 'serviciosapp/cliente.html'  # Asegúrate de tener este template creado
    context_object_name = 'cliente_list'  # Nombre del contexto que se usará en el template
    
    
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'serviciosapp/crearCliente.html'  # Asegúrate de tener este template creado
    success_url = reverse_lazy('vista_admin')  # Asegúrate de tener 'cliente-list' como el nombre correcto de tu vista de lista de clientes



        

class HomeView2(TemplateView):
    template_name = "serviciosapp/home2.html"

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
    