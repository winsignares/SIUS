from django.db import models
from home.models.carga_academica.datos_adicionales import Programa, Semestre
from home.models.talento_humano.tipo_documentos import TipoDocumento

# Create your models here.
class Estudiantes(models.Model):

    estudiante = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    fk_tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, default=0)
    numero_documento = models.BigIntegerField(unique=True, default=0)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, null=True, blank=True)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self):
        return f"{self.id} - {self.estudiante.username} - {self.programa.programa} - {self.semestre.descripcion}"