from django.db import models
from dashboard_talento_humano.models.niveles_academicos import NivelAcademico

class Tarifa(models.Model):
    nivel_academico = models.ForeignKey(NivelAcademico, on_delete=models.CASCADE, related_name="tarifas")
    anios_experiencia_min = models.PositiveIntegerField()
    anios_experiencia_max = models.PositiveIntegerField()
    tarifa_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
    vigencia = models.PositiveIntegerField()

    class Meta:
        db_table = 'tarifas'
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'
        unique_together = ('nivel_academico', 'anios_experiencia_min', 'anios_experiencia_max', 'vigencia') # Evita duplicados para el mismo nivel académico, experiencia y año

    def __str__(self):
        return f"{self.nivel_academico.nombre} ({self.vigencia}) - {self.anios_experiencia_min}-{self.anios_experiencia_max} años - ${self.tarifa_por_hora}/hora"
