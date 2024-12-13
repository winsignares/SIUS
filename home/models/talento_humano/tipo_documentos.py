from django.db import models


class TipoDocumento(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_documento = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tipo_documentos'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'

    def __str__(self):
        return f"{self.tipo_documento} - {self.descripcion}"
