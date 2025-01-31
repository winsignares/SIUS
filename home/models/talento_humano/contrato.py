from django.db import models
from .usuarios import Usuario

# Create your models here.


class Contrato(models.Model):
    id = models.AutoField(primary_key=True)
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="contrato", verbose_name=("Usuario"))
    fecha_inicio = models.DateField(verbose_name=('Fecha Inicio Contrato'), null=True, blank=True)
    fecha_fin = models.DateField(verbose_name=('Fecha Fin Contrato'), null=True, blank=True)
    tipo_contrato = models.CharField(verbose_name=('Tipo Contrato'), max_length=255, null=True, blank=True)
    dias_contrato = models.IntegerField(verbose_name=('Cantidad de Dias'), null=True, blank=True)

    class Meta:
        db_table = 'contrato'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return f"{self.fk_usuario.primer_nombre} {self.fk_usuario.primer_apellido} | Inicio: {self.fecha_inicio} Fin: {self.fecha_fin}"
