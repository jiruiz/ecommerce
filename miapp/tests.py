
from decimal import Decimal
from django.urls import reverse
from django.test import Client, TestCase
from miapp.forms import DatosFacturacionForm, DatosPersonalesForm, RegistroForm

# Create your tests here.

from miapp.models import Articulo, ArticuloCompra, DatosFacturacion, DatosPersonales, ItemCarrito, Compra, Usuario

from django.contrib.auth.models import User

class ItemCarritoTestCase(TestCase):
    # Configuración inicial para las pruebas
    def setUp(self):
        # Crea un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # Crea un artículo de prueba
        self.articulo = Articulo.objects.create(
            nombre='Articulo de prueba',
            precio=10.0,
            descripcion='Descripción de prueba',
            tipoCategoria='Computacion'
        )

    # Prueba la función que calcula el precio total del artículo en el carrito
    def test_precio_total(self):
        # Crea un item de carrito asociado al usuario y al artículo de prueba, con cantidad 3
        item_carrito = ItemCarrito.objects.create(
            usuario=self.user,
            articulo=self.articulo,
            cantidad=3
        )
        
        # Comprueba si el precio total calculado del item de carrito es 30.0 (10.0 * 3)
        self.assertEqual(item_carrito.precio_total(), 30.0)


class CompraTestCase(TestCase):
    def setUp(self):
        # Crea un usuario
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # Crea un objeto DatosPersonales asociado al usuario
        datos_personales = DatosPersonales.objects.create(
            nombre='Nombre',
            apellido='Apellido',
            correo='correo@example.com',
            telefono='123456789',
            claseFiscalTipo='Consumidor Final',
            numeroDocumento='1234567890',
            user=self.user
        )
        
        # Crea un objeto DatosFacturacion
        datos_facturacion = DatosFacturacion.objects.create(
            calle='Calle',
            altura='123',
            piso='2',
            departamento='B',
            codigoPostal='12345',
            localidad='Ciudad'
        )

        # Crea un objeto Usuario asociado al usuario y a los datos de facturación y personales
        self.usuario = Usuario.objects.create(
            idUsuario=1,
            # otros campos de Usuario
            datosPersonales=datos_personales,
            datosFacturacion=datos_facturacion
        )

    

class MiPrueba(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Iniciar sesión con el usuario
        self.client.login(username='testuser', password='password123')
        # Resto de la configuración de la prueba...




class ConfirmacionPagoTestCase(TestCase):
    def setUp(self):
        # Crea un usuario de prueba y otros datos necesarios para la prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('confirmacion')  
        
        # Crea un objeto Articulo de prueba
        self.articulo = Articulo.objects.create(nombre='Articulo de prueba', precio=10.0)

    def test_confirmacion_pago(self):
        # Crea un objeto ItemCarrito de prueba
        item_carrito = ItemCarrito.objects.create(usuario=self.user, articulo=self.articulo, cantidad=1)

        # Simula el contenido del formulario
        data = {
            'total_carrito': '10.0'  # Asegúrate de que este valor coincida con el precio del artículo
        }

        # Realiza una solicitud POST a la vista de confirmación
        response = self.client.post(self.url, data)

        # Verifica que la respuesta tenga código 200 (OK)
        self.assertEqual(response.status_code, 200)




class RegistroUsuarioTestCase(TestCase):
    def test_registro_usuario(self):
        # Aca estamos definiendo los datos de prueba para el formulario de registro para registrarse en la web
        datos_registro = {
            'username': 'nuevousuario',
            'password1': 'contraseña123',
            'password2': 'contraseña123',
        }
        
        # verificamos mediante POST a la vista de registro, con los datos de prueba de 'datos_registro'
        response = self.client.post(reverse('registro'), datos_registro)
        
        # Verifica que la respuesta tenga un código de estado 200 (redirección exitosa)
        self.assertEqual(response.status_code, 302)
        
        # Verifica que el usuario se haya creado correctamente en la base de datos
        usuario_creado = User.objects.filter(username='nuevousuario').first()
        self.assertIsNotNone(usuario_creado)
        


        # Verifica que el usuario sea redirigido correctamente después del registro (código de estado 302)
        self.assertRedirects(response, reverse('home'))


