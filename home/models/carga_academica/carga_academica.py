from django.db import models
from home.models.talento_humano.usuarios import Usuario
from .datos_adicionales import Periodo, Programa, Semestre, Materia


class CargaAcademica(models.Model):
    id = models.AutoField(primary_key=True)
    fk_periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    fk_programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    fk_semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    fk_materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    fk_docente_asignado = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    horas_asignadas = models.CharField(max_length=255, null=True, blank=True)
    materia_compartida = models.BooleanField(default=False)

    class Meta:
        db_table = 'cargas_academicas'
        verbose_name = 'Carga Acádemica'
        verbose_name_plural = 'Cargas Acádemicas'

    def __str__(self):
        return f"{self.fk_docente_asignado} {self.fk_materia}"
