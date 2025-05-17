from django.db import models
from ..talento_humano import Usuario

class Periodo(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField("Año", max_length=255, unique=True)
    periodo = models.CharField("Periodo", max_length=255, null=True, blank=True)
    fecha_apertura = models.DateField("Fecha de Apertura", null=True, blank=True)
    fecha_cierre = models.DateField("Fecha de Cierre", null=True, blank=True)
    salario_minimo = models.IntegerField("Salario Mínimo", null=True, blank=True)
    auxilio_transporte = models.IntegerField("Auxilio de Transporte", null=True, blank=True)

    class Meta:
        db_table = 'periodos'
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'

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
    horas = models.IntegerField("Total de Horas", null=True, blank=True)
    fk_programa = models.ForeignKey(Programa, verbose_name="Programa al que Pertenece", on_delete=models.CASCADE, null=True, blank=True)
    fk_pensum = models.ForeignKey(Pensum, verbose_name="Pensum al que Pertenece", on_delete=models.CASCADE, null=True, blank=True)
    fk_semestre = models.ForeignKey(Semestre, verbose_name="Semestre al que Pertenece", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return f" ({self.codigo}) {self.materia} - Créditos: {self.creditos}"


class Matricula(models.Model):
    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'fk_rol__rol': 'E'}
    )
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    fecha_matricula = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estudiante} matriculado en {self.materia}"

    class Meta:
        db_table = 'Matricula'
        unique_together = ('estudiante', 'materia')
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        


class Prerrequisito(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='materia_principal')
    prerequisito = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='materia_requerida')

    def __str__(self):
        return f"{self.materia.codigo} requiere {self.prerequisito.codigo}"

    class Meta:
        db_table = 'Prerrequisito'
        unique_together = ('materia', 'prerequisito')
        verbose_name = "Prerrequisito"
        verbose_name_plural = "Prerrequisitos"



class MateriaAprobada(models.Model):
    ESTADO_OPCIONES = [
        ('aprobada', 'Aprobada'),
        ('reprobada', 'Reprobada'),
    ]

    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'fk_rol__rol': 'E'}
    )
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    estado_aprobacion = models.CharField(max_length=10, choices=ESTADO_OPCIONES)

    def __str__(self):
        return f"{self.estudiante} cursó {self.materia} desde {self.fecha_inicio} hasta {self.fecha_finalizacion} - Estado: {self.estado_aprobacion}"

    class Meta:
        db_table = 'materia_cursada'
        unique_together = ('estudiante', 'materia')
        verbose_name = "Materia Cursada"
        verbose_name_plural = "Materias Cursadas"

class HistorialAcademico(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'fk_rol__rol': 'E'})
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=4, decimal_places=2)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, choices=[('Aprobado', 'Aprobado'), ('Reprobado', 'Reprobado')])

class MateriaDocente(models.Model):
    docente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'fk_rol__rol': 'D'},
        verbose_name="Docente asignado"
    )
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, verbose_name="Materia asignada")
    fecha_asignacion = models.DateField("Fecha de asignación", auto_now_add=True)

    class Meta:
        db_table = 'materias_docentes'
        unique_together = ('docente', 'materia')
        verbose_name = "Materia-Docente"
        verbose_name_plural = "Materias-Docentes"

    def __str__(self):
        return f"{self.docente} asignado a {self.materia}"
