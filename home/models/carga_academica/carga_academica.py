from django.db import models
from home.models.talento_humano.usuarios import Usuario
from .datos_adicionales import Periodo, Programa, Semestre, Materia


class CargaAcademica(models.Model):
    id = models.AutoField(primary_key=True)
    fk_periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, verbose_name= "Periodo")
    fk_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, verbose_name= "Programa")
    fk_semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, verbose_name= "Semestre")
    fk_materia = models.ForeignKey(Materia, on_delete=models.CASCADE, verbose_name= "Materia")
    fk_docente_asignado = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name= "Docente Asignado")
    horas_semanales = models.CharField("Horas Semanales", max_length=255, null=True, blank=True)
    valor_a_pagar = models.IntegerField("Valor a Pagar", null=True, blank=True)
    materia_compartida = models.BooleanField("Materia Compartida", default=False)
    aprobado = models.BooleanField("Aprobado", default=False)

    class Meta:
        db_table = 'cargas_academicas'
        verbose_name = 'Carga Acádemica'
        verbose_name_plural = 'Cargas Acádemicas'

    def __str__(self):
        return f"{self.fk_materia}: {self.fk_docente_asignado} - Horas: {self.horas_semanales} - Valor a Pagar: ${self.valor_a_pagar}"
