from django.db import models


class Periodo(models.Model):
    id = models.AutoField(primary_key=True)
    periodo = models.CharField(max_length=255, unique=True)
    fecha_apertura = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'periodos'
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'

    def __str__(self):
        return f"{self.periodo} | Fecha Apertura: {self.fecha_apertura} - Fecha Cierre: {self.fecha_cierre}"


class Programa(models.Model):
    id = models.AutoField(primary_key=True)
    codigo_snies = models.CharField(max_length=255, unique=True)
    nivel_formacion = models.CharField(max_length=255, null=True, blank=True)
    programa = models.CharField(max_length=255, null=True, blank=True)
    sede = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'programas'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return f"{self.codigo} - {self.programa}"


class Semestre(models.Model):
    id = models.AutoField(primary_key=True)
    semestre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'semestres'
        verbose_name = 'Semestre'
        verbose_name_plural = 'Semestres'

    def __str__(self):
        return f"{self.semestre}"


class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=255, unique=True)
    materia = models.CharField(max_length=255, null=True, blank=True)
    credito = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return f" {self.codigo} - {self.materia}"
