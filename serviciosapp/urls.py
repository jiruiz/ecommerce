from django.urls import path
from .views import ClienteListView,ClienteCreateView,HomeView2

urlpatterns = [
    path('cliente/', ClienteListView.as_view(), name='cliente'),
    # Otra URLs de tu aplicación serviciosapp aquí....
    path('crearCliente/', ClienteCreateView.as_view(), name='crearCliente'),
    path('home2/', HomeView2.as_view(), name='home2'),

]
