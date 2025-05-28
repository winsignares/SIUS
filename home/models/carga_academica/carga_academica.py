from django.db import models
from home.models.talento_humano.usuarios import Empleado
from .datos_adicionales import Periodo, Programa, Semestre, Materia
from django.conf import settings


class CargaAcademica(models.Model):
    id = models.AutoField(primary_key=True)
    fk_periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, verbose_name="Periodo")
    fk_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, verbose_name="Programa")
    fk_semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, verbose_name="Semestre")
    fk_materia = models.ForeignKey(Materia, on_delete=models.CASCADE, verbose_name="Materia")
    fk_docente_asignado = models.ForeignKey(Empleado, on_delete=models.CASCADE, verbose_name="Docente Asignado")
    horas_semanales = models.CharField("Horas Semanales", max_length=255, null=True, blank=True)
    total_horas = models.CharField("Total Horas", max_length=255, null=True, blank=True)
    valor_a_pagar = models.IntegerField("Valor a Pagar", null=True, blank=True)
    materia_compartida = models.BooleanField("Materia Compartida", default=False, null=True, blank=True)

    # Creación de carga académica
    fk_creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='carga_academica_creado_por', verbose_name="Creado Por", on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField("Fecha Creación", auto_now_add=True, null=True, blank=True)

    # Modificación de la carga académica
    fk_modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='carga_academica_modificado_por', verbose_name="Modificado Por", on_delete=models.SET_NULL, null=True, blank=True)
    fecha_modificacion = models.DateTimeField("Fecha Modificación", auto_now=True, null=True, blank=True)

    # Aprobación vicerectoria
    aprobado_vicerrectoria = models.BooleanField("Aprobado", default=False)
    fk_aprobado_vicerrectoria = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='aprobacion_vicerrectoria',verbose_name="Aprobación Vicerrectoria", on_delete=models.SET_NULL, null=True, blank=True)
    fecha_aprobacion_vicerrectoria = models.DateTimeField("Fecha Aprobación Vicerrectoria", auto_now_add=True, null=True, blank=True)

    # Aprobación Contabilidad
    aprobado_contabilidad = models.BooleanField("Aprobado", default=False)
    fk_aprobado_contabilidad = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='aprobacion_contabilidad', verbose_name="Aprobación Contabilidad", on_delete=models.SET_NULL, null=True, blank=True)
    fecha_aprobacion_contabilidad = models.DateTimeField("Fecha Aprobación Contabilidad", auto_now_add=True, null=True, blank=True)

    # Aprobación Rectoría
    aprobado_rectoria = models.BooleanField("Aprobado", default=False)
    fk_aprobado_rectoria = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='aprobacion_rectoria', verbose_name="Aprobación Rectoría", on_delete=models.SET_NULL, null=True, blank=True)
    fecha_aprobacion_rectoria = models.DateTimeField("Fecha Aprobación Rectoría", auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'cargas_academicas'
        verbose_name = 'Carga Acádemica'
        verbose_name_plural = 'Cargas Acádemicas'

    def __str__(self):
        return f"{self.fk_materia}: {self.fk_docente_asignado} - Horas: {self.horas_semanales} - Valor a Pagar: ${self.valor_a_pagar}"


class MateriaCompartida(models.Model):
    id = models.AutoField(primary_key=True)
    fk_carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, verbose_name="Carga Académica")
    fk_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, verbose_name="Programa")
    fk_periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, verbose_name="Periodo")

    class Meta:
        db_table = 'materias_compartidas'
        verbose_name = 'Materia Compartida'
        verbose_name_plural = 'Materias Compartidas'

    def __str__(self):
        return f"{self.fk_carga_academica} - {self.fk_docente_asignado} - Horas: {self.horas_semanales} - Valor a Pagar: ${self.valor_a_pagar}"


class FuncionesSustantivas(models.Model):
    fk_carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, verbose_name="Carga Académica")
    horas_administrativas = models.IntegerField("Horas por Administrativas", null=True, blank=True)
    horas_docencia = models.IntegerField("Horas por Docencia", null=True, blank=True)
    horas_investigacion = models.IntegerField("Horas por Investigación", null=True, blank=True)
    horas_otras_actividades = models.IntegerField("Horas por Otras Actividades", null=True, blank=True)
    horas_proyeccion_extension = models.IntegerField("Horas por Proyección y Extensión", null=True, blank=True)

    class Meta:
        db_table = "funciones_sustantivas"
        verbose_name = "FuncionesSustantivas"
        verbose_name_plural = "FuncionesSustantivass"

    def __str__(self):
        return self.name
