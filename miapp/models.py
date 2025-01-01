from django.db import models
from django.contrib.auth.models import User

class DatosPersonales(models.Model):
    idDatosPersonales = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    CLASE = [   
        ("Consumidor Final", "Consumidor Final"),
        ("Monotributo", "Monotributo"),
        ("Responsable Inscripto", "Responsable Inscripto"),
        ("Excento", "Excento")
    ]
    claseFiscalTipo = models.CharField(max_length=30, choices=CLASE)
    numeroDocumento = models.CharField(max_length=20)
    # Agrega un campo para la relación con el usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = "Dato Personal"
        verbose_name_plural = "Datos Personales"
        ordering = ["nombre", "claseFiscalTipo"]

    def save(self, *args, **kwargs):
        # Asigna el usuario actual al campo 'user' antes de guardar
        if not self.user_id:
            self.user = User.objects.get(username='nombre_de_usuario_actual')
        super().save(*args, **kwargs)

class DatosFacturacion(models.Model):
    idDatosFacturacion = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calle = models.CharField(max_length=100)
    altura = models.CharField(max_length=10)
    piso = models.CharField(max_length=10, blank=True)
    departamento = models.CharField(max_length=10, blank=True)
    codigoPostal = models.CharField(max_length=10)
    localidad = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.idDatosFacturacion}"
    class Meta:
        verbose_name= "Dato Facturacion"
        verbose_name_plural = "Datos de Facturación"



# ////////////////// - NO LO ESTOY USANDO - //////////////////////
class Comprobante(models.Model):
    idComprobante = models.AutoField(primary_key=True)
    numeroComprobante = models.CharField(max_length=20, verbose_name="Número de Comprobante")
    fechaEmision = models.DateField()
    # Otros campos relacionados con la factura
    def __str__(self):
        return f"{self.numeroComprobante}"
    class Meta:
        verbose_name= "Comprobante"
        verbose_name_plural = "Comprobantes"

class Usuario(models.Model):
    idUsuario = models.AutoField(primary_key=True)
    datosPersonales = models.OneToOneField(DatosPersonales, on_delete=models.CASCADE)
    datosFacturacion = models.OneToOneField(DatosFacturacion, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.idUsuario}"



    class Meta:
        verbose_name= "Usuarios"
        verbose_name_plural = "Usuarios"

# ////////////////// - HASTA ACA NO LO ESTOY USANDO - //////////////////////



class Articulo(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    image = models.ImageField(upload_to="articulos", null=True, blank=True, verbose_name="Ilustración")
    image2 = models.ImageField(upload_to="articulos", null=True, blank=True, verbose_name="Ilustración2")
    image3 = models.ImageField(upload_to="articulos", null=True, blank=True, verbose_name="Ilustración3")
    image4 = models.ImageField(upload_to="articulos", null=True, blank=True, verbose_name="Ilustración4")
    stock = models.PositiveIntegerField(default=0)
    CATEGORIA = [   
        ("Computacion", "Computación"),
        ("Componentes", "Componentes"),
        ("Accesorios", "Accesorios"),
        
    ]
    tipoCategoria = models.CharField(max_length=30, choices=CATEGORIA)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"



class Compra(models.Model):
    idCompra = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)  # Agrega este campo
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    articulos = models.ManyToManyField(Articulo, through='ArticuloCompra')
    

    def __str__(self):
        return f"Compra #{self.idCompra}"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"






class ArticuloCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)  # Puedes ajustar esto según tus necesidades

    def __str__(self):
        return f"{self.cantidad}u. x {self.articulo.nombre}"

    class Meta:
        verbose_name = "Artículo en Compra"
        verbose_name_plural = "Artículos en Compras"


class ItemCarrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Asociado a un usuario autenticado
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def precio_total(self):
        return self.cantidad * self.articulo.precio

    def __str__(self):
        return f"{self.cantidad} x {self.articulo.nombre}"
    

class Factura(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    datosFacturacion = models.ForeignKey(DatosFacturacion, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    
    
    
    
    