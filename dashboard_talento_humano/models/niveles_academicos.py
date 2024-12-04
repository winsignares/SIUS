from django.db import models

class NivelAcademico(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)  #Bachiller, Técnico Profesional, Tecnólogo, Profesional Académico, Especialización, Maestría, Doctorado, Posdoctorado
    tarifa_base_por_hora = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'niveles_academicos'
        verbose_name = 'Nivel Académico'
        verbose_name_plural = 'Niveles Académicos'

    def __str__(self):
        return f"{self.nombre} - ${self.tarifa_base_por_hora}/hora"