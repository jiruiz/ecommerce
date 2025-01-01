from django.contrib import admin
from django.utils.safestring import mark_safe

from miapp.forms import ArticuloForm

from .models import *
# Register your models here.





class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = ('idDatosPersonales','user', 'claseFiscalTipo', 'numeroDocumento')

class NuevaFacturaAdmin(admin.ModelAdmin):
    list_display = ('id','created', 'datosFacturacion', 'compra')


class DatosFacturacionAdmin(admin.ModelAdmin):
    list_display = ('idDatosFacturacion', 'user', 'calle', 'altura',  'codigoPostal', 'localidad')

class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('idComprobante', 'numeroComprobante', 'fechaEmision')

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('idUsuario', 'datosPersonales', 'datosFacturacion')


class CompraAdmin(admin.ModelAdmin):
    
    
    def mostrar_articulos(self, obj):
        return ", ".join([str(articulo) for articulo in obj.articulos.all()])

    mostrar_articulos.short_description = 'Artículos'
    list_display = ('idCompra', 'fecha', 'monto', 'usuario','mostrar_articulos')


class ArticuloAdmin(admin.ModelAdmin):
    form = ArticuloForm

    list_display = ('id','nombre', 'precio', 'descripcion_preview', 'image', 'image2', 'image3', 'image4')

    def descripcion_preview(self, obj):
        # Utiliza mark_safe para renderizar el HTML en el campo de descripción
        return mark_safe(obj.descripcion[:100] + '...')  # Mostrar los primeros 100 caracteres
    descripcion_preview.short_description = 'Descripción'


class ArticuloCompraAdmin(admin.ModelAdmin):
    pass

class AgregarAdmin(admin.ModelAdmin):
    list_display = ('id','usuario' ,'articulo', 'cantidad')

admin.site.register(DatosPersonales, DatosPersonalesAdmin)
admin.site.register(DatosFacturacion, DatosFacturacionAdmin)
admin.site.register(Comprobante, ComprobanteAdmin)
admin.site.register(Compra, CompraAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(ArticuloCompra, ArticuloCompraAdmin)
admin.site.register(ItemCarrito, AgregarAdmin)
admin.site.register(Factura, NuevaFacturaAdmin)