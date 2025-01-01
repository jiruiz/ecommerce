from django.db import models

# Create your models here.
class Cliente(models.Model):
    idCliente = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=100)
    telefono =  models.CharField(max_length=100)
    correo = models.EmailField()
    def __str__(self):
        return f"{self.nombre}"
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Cliente"
