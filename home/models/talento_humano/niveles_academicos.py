from django.db import models

class NivelAcademico(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)  #Bachiller, Técnico Profesional, Tecnólogo, Profesional Académico, Especialización, Maestría, Doctorado, Posdoctorado
    descripcion = models.TextField(null=True, blank=True)
    tarifa_base_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
    vigencia = models.PositiveIntegerField()

    class Meta:
        db_table = 'niveles_academicos'
        verbose_name = 'Nivel Académico'
        verbose_name_plural = 'Niveles Académicos'
        unique_together = ('nombre', 'vigencia') # Evita duplicados para el mismo nivel académico y año

    def __str__(self):
        return f"{self.nombre} ({self.vigencia}) - ${self.tarifa_base_por_hora}/hora"