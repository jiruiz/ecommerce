from django.urls import path, include


# en el * se encuentra el HomeView
from .views import *
from miapp import views
from django.contrib.auth.views import LogoutView
from .views import ArticuloDetailView, SearchView, ArticuloUpdate, CambiarClaveView, VerCarritoView, NoRegistradoView,RegistroDatosPersonales
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.views.decorators.http import require_http_methods
from miapp.views import RegistroUsuario
# aca van nuestras paginas 



urlpatterns = [
  
    # path('', HomeView.as_view() ,  name="index"),
    path('', HomeView.as_view() ,  name="home"),
    path('compras/', Compras.as_view() ,  name="compras"),
    path('usuarios/', UsuariosList.as_view() ,  name="usuarios"),
    path('datos/', DatosPersonalesList.as_view() ,  name="datos"),
    path('facturacion/', DatosFacturacionList.as_view() ,  name="facturacion"),
    path('articulo_create/',  ArticuloCreate.as_view(), name="articulo-create"),
    path('articulos/',  ArticuloView.as_view(), name="articulos"),
    path('agregar_al_carrito/<int:articulo_id>/', AgregarAlCarritoView.as_view(), name='agregar_al_carrito'),
    path('ver_carrito/', VerCarritoView.as_view(), name='ver_carrito'),
    path('login/',  MyLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(next_page="home"), name="logout"),
    path('registro/', RegistroUsuario.as_view(), name="registro"),
    path('aumentar/<int:item_id>/', AumentarCantidadView.as_view(), name='aumentar'),
    path('disminuir/<int:item_id>/', DisminuirCantidadView.as_view(), name='disminuir'),
    path('eliminar/<int:item_id>/', EliminarDelCarritoView.as_view(), name='eliminar'),
    path('pagar/', IrAPagarView.as_view(), name='pagar'), 
    path('cancelar/', CancelarCompraView.as_view(), name='cancelar'), 
    path('registroDatosPersonales/', RegistroDatosPersonales.as_view(), name='registroDatosPersonales'),  
    path('articulo/<int:pk>/', ArticuloDetailView.as_view(), name='articulo-detail'),
    path('search/', SearchView.as_view(), name="search"),
    path('articulo_update/<int:pk>/', ArticuloUpdate.as_view(), name="articulo-update"),
    path('articulo_delete/<int:pk>/',  ArticuloDelete.as_view(), name="articulo-delete"),


    path('miapp/datosFacturacion.html', CrearDatosFacturacionView.as_view(), name='datos_facturacion'),
    path('cambiar-clave/<int:usuario_id>/', views.CambiarClaveView.as_view(), name='cambiar_clave'),
    path('no_registrado/', NoRegistradoView.as_view(), name='no_registrado'),
    path('iniciar_pago/', NoRegistradoView.as_view(), name='iniciar_pago'),
    # path('pago/', PagoMP.as_view(), name='pago'),       
    # path('error/', PaginaError.as_view(), name='error'),

    # path('confirmacion/<str:total_carrito>/<int:usuario_id>/', views.ConfirmacionPago.as_view(), name='confirmacion'),
    path('confirmacion/', views.ConfirmacionPago.as_view(), name='confirmacion'),
    path('ver-datos-usuario/', views.ver_datos_usuario, name='verDatosUsuario'),
    path('datospersonales-update/<int:pk>/',  DatosPersonalesUpdate.as_view(), name="datospersonales-update"),
    path('datosfacturacion-update/<int:pk>/',  DatosFactuacionUpdate.as_view(), name="datosfacturacion-update"),
    path('base',  BaseView.as_view(), name="base"),
    path('compras',  CompraListView.as_view(), name="compras"),

    path('compra-update/<int:pk>/',  CompraUpdate.as_view(), name="compra-update"),
    path('compra_delete/<int:pk>/',  CompraDelete.as_view(), name="compra-delete"),
    path('load_modal_content/', views.load_modal_content, name='load_modal_content'),
    path('listausuarios/', MostrarUsuariosView.as_view(), name='listausuarios'),
    path('guardar_usuario/<int:usuario_id>/', views.guardar_usuario, name='guardar-usuario'),
    path('vista_admin/',VistaAdmin.as_view(), name='vista_admin'),
    path('base1/', VistaBase.as_view(), name='base1'),
    path('detalle/<int:pk>/', VistaDetalle.as_view(), name='detalle'),

    path('accesorios/', AccesoriosListView.as_view(), name='accesorios'),
    path('componentes/', ComponentesListView.as_view(), name='componentes'),
    path('computacion/', ComputacionListView.as_view(), name='computacion'),
    path('ver_compras/', VerComprasView.as_view(), name='ver_compras'),
    path('compra_detail/<int:pk>/', VerCompraDetail.as_view(), name='compra_detail'),
    path('factura/<int:pk>/', FacturaView.as_view(), name='factura'),
    path('factura/<int:pk>/factura_print/', FacturaPrintView.as_view(), name='factura_print'),
    #path('compra-confirmada/', CompraConfirmadaView.as_view(), name='compra-confirmada'),
    path('perfil', PerfilView.as_view(), name='perfil'),
    path('control_stock/', ControlStockView.as_view(), name='control_stock'),
    path('nuevaFactura/', FacturaNuevaView.as_view(), name='nuevaFactura'),
    
    ]








































































































































































