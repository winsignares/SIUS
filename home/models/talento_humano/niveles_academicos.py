from django.db import models


class NivelAcademico(models.Model):
    id = models.AutoField(primary_key=True)

    # Bachiller, Técnico Profesional, Tecnólogo, Profesional Académico, Especialización, Maestría, Doctorado, Posdoctorado
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'niveles_academicos'
        verbose_name = 'Nivel Académico'
        verbose_name_plural = 'Niveles Académicos'

    def __str__(self):
        return f"{self.nombre}"


class NivelAcademicoHistorico(models.Model):
    id = models.AutoField(primary_key=True)
    fk_nivel_academico = models.ForeignKey(NivelAcademico, on_delete=models.CASCADE)
    tarifa_base_por_hora = models.DecimalField(max_digits=10, decimal_places=2)
    año_vigencia = models.PositiveIntegerField()

    class Meta:
        db_table = 'niveles_academicos_historico'
        verbose_name = 'Nivel Académico Histórico'
        verbose_name_plural = 'Niveles Académicos Históricos'
        unique_together = ('fk_nivel_academico', 'año_vigencia')

    def __str__(self):
        return f"{self.fk_nivel_academico.nombre} - ${self.tarifa_base_por_hora} - {self.vigencia}"
