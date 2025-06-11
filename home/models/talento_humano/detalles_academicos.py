from django.db import models
from .usuarios import Empleado
from .niveles_academicos import NivelAcademico


class DetalleAcademico(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="detalles_academicos")
    nivel_academico = models.ForeignKey(NivelAcademico, on_delete=models.CASCADE)
    institucion = models.CharField(max_length=255)
    institucion_extranjera = models.CharField(max_length=255, null=True, blank=True)
    codigo_convalidacion = models.CharField(max_length=50, null=True, blank=True)
    titulo_obtenido = models.CharField(max_length=255)
    metodologia_programa = models.CharField(max_length=50, null=True, blank=True)
    ies_codigo = models.PositiveIntegerField(null=True, blank=True)
    codigo_pais = models.PositiveIntegerField(null=True, blank=True)
    fecha_graduacion = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'detalles_academicos'
        verbose_name = 'Detalle Académico'
        verbose_name_plural = 'Detalles Académicos'

    def __str__(self):
        return f"{self.usuario} - {self.nivel_academico.nombre} - {self.titulo_obtenido}"
