from django.db import models
from home.models.carga_academica.datos_adicionales import Materia
from home.models.talento_humano import Empleado
from admisiones.models import Estudiantes
from django.contrib.auth.models import User
from home.models.carga_academica.datos_adicionales import Periodo


class CategoriaEstudiante(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categorias_estudiantes'
        verbose_name = 'Categoria Estudiantes'
        verbose_name_plural = 'Categorias Estudiantes'


class PreguntaEstudiante(models.Model):
    categoria = models.ForeignKey(
        CategoriaEstudiante,
        on_delete=models.CASCADE,
        related_name="preguntas"
    )
    texto = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.texto

    class Meta:
        db_table = 'preguntas_estudiantes'
        verbose_name = 'Pregunta Estudiantes'
        verbose_name_plural = 'Preguntas Estudiantes'


class CategoriaDocente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categorias_docentes'
        verbose_name = 'Categoria Docentes'
        verbose_name_plural = 'Categorias Docentes'


class PreguntaDocente(models.Model):
    categoria = models.ForeignKey(
        CategoriaDocente,
        on_delete=models.CASCADE,
        related_name="preguntas"
    )
    texto = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.texto

    class Meta:
        db_table = 'preguntas_docentes'
        verbose_name = 'Pregunta Docentes'
        verbose_name_plural = 'Preguntas Docentes'


class CategoriaDirectivo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categorias_directivos'
        verbose_name = 'Categoria Directivos'
        verbose_name_plural = 'Categorias Directivos'


class PreguntaDirectivo(models.Model):
    categoria = models.ForeignKey(
        CategoriaDirectivo,
        on_delete=models.CASCADE,
        related_name="preguntas"
    )
    texto = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.texto

    class Meta:
        db_table = 'preguntas_directivos'
        verbose_name = 'Pregunta Directivos'
        verbose_name_plural = 'Preguntas Directivos'


class CategoriaDocentePostgrado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categorias_docentes_postgrado'
        verbose_name = 'Categoria Docente Postgrado'
        verbose_name_plural = 'Categorias Docentes Postgrado'


class PreguntaDocentePostgrado(models.Model):
    categoria = models.ForeignKey(
        CategoriaDocentePostgrado,
        on_delete=models.CASCADE,
        related_name="preguntas"
    )
    texto = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.texto

    class Meta:
        db_table = 'preguntas_docentes_postgrado'
        verbose_name = 'Pregunta Docente Postgrado'
        verbose_name_plural = 'Preguntas Docentes Postgrado'


class EvaluacionEstudiante(models.Model):
    estudiante = models.ForeignKey(
        Estudiantes,
        on_delete=models.CASCADE,
        related_name='evaluaciones'
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='evaluaciones'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='evaluaciones_estudiantes'
    )
    docente_evaluado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='evaluaciones_estudiantes_docentes',
        limit_choices_to={'fk_rol__rol': 'D'}
    )

    respuestas = models.JSONField(
        help_text="Diccionario con claves de pregunta_id y valores con respuesta")
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.estudiante} en {self.materia} durante {self.periodo}"

    class Meta:
        db_table = 'evaluacion_estudiante'
        verbose_name = 'Evaluación Estudiante'
        verbose_name_plural = 'Evaluaciones Estudiantes'
        unique_together = ('estudiante', 'materia', 'periodo')


class EvaluacionDocente(models.Model):
    docente = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='evaluaciones_docente'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='evaluaciones_docentes'
    )
    respuestas = models.JSONField(
        help_text="Diccionario con claves de pregunta_id y valores con respuesta")
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Autoevaluación de {self.docente} en {self.periodo}"

    class Meta:
        db_table = 'evaluacion_docente'
        verbose_name = 'Evaluación Docente'
        verbose_name_plural = 'Evaluaciones Docentes'
        unique_together = ('docente', 'periodo')


class EvaluacionDocentePostgrado(models.Model):
    docente = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='evaluaciones_docente_postgrado'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='evaluaciones_docentes_postgrado'
    )
    respuestas = models.JSONField(
        help_text="Diccionario con claves de pregunta_id y valores con respuesta")
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Autoevaluación de {self.docente} en {self.periodo}"

    class Meta:
        db_table = 'evaluacion_docente_postgrado'
        verbose_name = 'Evaluación Docente Postgrado'
        verbose_name_plural = 'Evaluaciones Docentes De Postgrado'
        unique_together = ('docente', 'periodo')


class EvaluacionDirectivo(models.Model):
    evaluador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='evaluaciones_directivo'
    )
    docente_evaluado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='evaluaciones_directivos',
        limit_choices_to={'fk_rol__rol': 'D'}
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='evaluaciones_directivos'
    )
    respuestas = models.JSONField(
        help_text="Diccionario con claves de pregunta_id y valores con respuesta")
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.docente_evaluado} por {self.evaluador} en {self.periodo}"

    class Meta:
        db_table = 'evaluacion_directivo'
        verbose_name = 'Evaluación Directivo'
        verbose_name_plural = 'Evaluaciones Directivos'
        unique_together = ('evaluador', 'docente_evaluado', 'periodo')
