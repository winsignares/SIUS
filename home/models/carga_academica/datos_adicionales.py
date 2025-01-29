from django.db import models
from django.utils.translation import gettext_lazy as _


class Periodo(models.Model):
    id = models.AutoField(primary_key=True)
    año = models.CharField(verbose_name=_("Año"), max_length=255, unique=True)
    periodo = models.CharField(verbose_name=_("Periodo"), max_length=255, null=True, blank=True)
    fecha_apertura = models.DateField(verbose_name=_("Fecha de Apertura"), null=True, blank=True)
    fecha_cierre = models.DateField(verbose_name=_("Fecha de Cierre"), null=True, blank=True)

    class Meta:
        db_table = 'periodos'
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'

    def __str__(self):
        return f"{self.año}-{self.periodo}"


class Programa(models.Model):
    id = models.AutoField(primary_key=True)
    codigo_snies = models.CharField(verbose_name=_("Código SNIES"), max_length=255, unique=True)
    nivel_formacion = models.CharField(verbose_name=_("Nivel de Formación"), max_length=255, null=True, blank=True)
    programa = models.CharField(verbose_name=_("Nombre del Programa"), max_length=255, null=True, blank=True)
    sede = models.CharField(verbose_name=_("Sede"), max_length=255, null=True, blank=True)
    numero_semestres = models.CharField(verbose_name=_("Número de Semestres"), max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'programas'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return f"(Código SNIES: {self.codigo_snies}) {self.programa} - {self.sede}"


class Semestre(models.Model):
    id = models.AutoField(primary_key=True)
    semestre = models.CharField(verbose_name=_("Semestre"), max_length=255, unique=True)
    descripcion = models.CharField(verbose_name=_("Descripción"),  max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'semestres'
        verbose_name = 'Semestre'
        verbose_name_plural = 'Semestres'

    def __str__(self):
        return f"{self.descripcion} Semestre"


class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(verbose_name=_("Código"), max_length=255, unique=True)
    materia = models.CharField(verbose_name=_("Materia"), max_length=255, null=True, blank=True)
    creditos = models.CharField(verbose_name=_("Número de Créditos"), max_length=255, null=True, blank=True)
    metodologia = models.CharField(verbose_name=_("Metodología"), max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return f" ({self.codigo}) {self.materia} - Créditos: {self.creditos}"
