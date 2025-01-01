from django.contrib import admin
from .models import *
# Register your models here.


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('idCliente','created', 'nombre', 'telefono','correo')
    
    
    
    
admin.site.register(Cliente, ClienteAdmin)    