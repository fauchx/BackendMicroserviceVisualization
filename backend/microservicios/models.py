from django.db import models

# Create your models here.
class Microservicio(models.Model):
    config_id = models.IntegerField(blank=False, null=False)
    historias = models.TextField()