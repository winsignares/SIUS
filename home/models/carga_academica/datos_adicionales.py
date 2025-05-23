from django.conf import settings
from django.db import models


class Periodo(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField("Año", max_length=255, null=True, blank=True)
    periodo = models.CharField("Periodo", max_length=255, null=True, blank=True)
    fecha_apertura = models.DateField("Fecha de Apertura", null=True, blank=True)
    fecha_cierre = models.DateField("Fecha de Cierre", null=True, blank=True)
    salario_minimo = models.IntegerField("Salario Mínimo", null=True, blank=True)
    auxilio_transporte = models.IntegerField("Auxilio de Transporte", null=True, blank=True)

    class Meta:
        db_table = 'periodos'
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'
        unique_together = ('year', 'periodo')

    def __str__(self):
        return f"{self.year}-{self.periodo}"


class Programa(models.Model):
    id = models.AutoField(primary_key=True)
    codigo_snies = models.CharField("Código SNIES", max_length=255, unique=True)
    programa = models.CharField("Nombre del Programa", max_length=255, null=True, blank=True)
    nivel_formacion = models.CharField("Nivel de Formación", max_length=255, null=True, blank=True)
    sede = models.CharField("Sede", max_length=255, null=True, blank=True)
    numero_semestres = models.CharField("Número de Semestres", max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'programas'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return f"(Código SNIES: {self.codigo_snies}) {self.nivel_formacion} en {self.programa} - {self.sede}"


class ProgramaUser(models.Model):

    fk_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='programa_user', verbose_name='Programa')
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_programa', verbose_name='User Asignado')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'programa_user'
        verbose_name = "ProgramaUser"
        verbose_name_plural = "ProgramaUsers"
        unique_together = ('fk_programa', 'fk_user')

    def __str__(self):
        return f'{self.fk_programa.programa} - {self.fk_user.username}'


class Pensum(models.Model):
    id = models.AutoField(primary_key=True)
    fk_programa = models.ForeignKey(Programa, verbose_name="Programa al que Pertenece", on_delete=models.CASCADE)
    codigo_pensum = models.IntegerField("Codigo Pensum", null=True, blank=True)
    vigente = models.BooleanField(default=False)

    class Meta:
        db_table = 'pensums'
        verbose_name = 'Pensum'
        verbose_name_plural = 'Pensums'

    def __str__(self):
        return f"Programa {self.fk_programa.programa}: {self.codigo_pensum} - Vigente: {self.vigente}"


class Semestre(models.Model):
    id = models.AutoField(primary_key=True)
    semestre = models.CharField("Semestre", max_length=255, unique=True)
    descripcion = models.CharField("Descripción",  max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'semestres'
        verbose_name = 'Semestre'
        verbose_name_plural = 'Semestres'

    def __str__(self):
        return f"{self.descripcion} Semestre"


class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField("Código", max_length=255, unique=True)
    materia = models.CharField("Materia", max_length=255, null=True, blank=True)
    creditos = models.CharField("Número de Créditos", max_length=255, null=True, blank=True)
    metodologia = models.CharField("Metodología", max_length=50, null=True, blank=True)
    horas_semanales = models.IntegerField("Horas Semanales", null=True, blank=True)
    fk_programa = models.ForeignKey(Programa, verbose_name="Programa al que Pertenece", on_delete=models.CASCADE, null=True, blank=True)
    fk_pensum = models.ForeignKey(Pensum, verbose_name="Pensum al que Pertenece", on_delete=models.CASCADE, null=True, blank=True)
    fk_semestre = models.ForeignKey(Semestre, verbose_name="Semestre al que Pertenece", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return f" ({self.codigo}) {self.materia} - Créditos: {self.creditos}"