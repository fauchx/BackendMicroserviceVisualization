from django.db import models

# Create your models here.
class Configuracion(models.Model):
    nombre_proyecto = models.CharField(max_length=100)
    cantidad_microservicios = models.IntegerField(blank=False, null=False)
    cantidad_historias = models.IntegerField(blank=False, null=False)
    json_info = models.TextField()