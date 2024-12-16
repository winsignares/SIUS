from django.db import models
from .usuarios import Usuario


class DetalleExperienciaLaboral(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="detalles_experiencia_laboral")
    empresa = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_fin = models.DateField(null=False, blank=False)

    class Meta:
        db_table = 'detalles_exp_laboral'
        verbose_name = 'Detalle Experiencia Laboral'
        verbose_name_plural = 'Detalles Experiencia Laboral'

    def __str__(self):
        return f"{self.usuario} - {self.cargo} en {self.empresa}"
