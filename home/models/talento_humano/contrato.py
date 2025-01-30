from django.db import models
from .usuarios import Usuario

# Create your models here.


class Contrato(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="contrato", verbose_name=("Usuario"))
    fecha_inicio = models.DateField(verbose_name=('Fecha Inicio Contrato') ,null=False, blank=False)
    fecha_fin = models.DateField(verbose_name=('Fecha Fin Contrato'), null=False, blank=False)
    tipo_contrato = models.CharField(verbose_name=('Tipo Contrato'), max_length=255, null=False, blank=False)
