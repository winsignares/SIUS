from django.db import models
from .usuarios import Usuario
from .niveles_academicos import NivelAcademico

class DetalleAcademico(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="detalles_academicos")
    nivel_academico = models.ForeignKey(NivelAcademico, on_delete=models.CASCADE)
    institucion = models.CharField(max_length=255)
    titulo_obtenido = models.CharField(max_length=255)
    fecha_graduacion = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'detalles_academicos'
        verbose_name = 'Detalle Académico'
        verbose_name_plural = 'Detalles Académicos'

    def __str__(self):
        return f"{self.usuario} - {self.nivel_academico.nombre} - {self.titulo_obtenido}"