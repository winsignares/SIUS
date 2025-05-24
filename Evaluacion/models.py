from django.db import models
from home.models.carga_academica.datos_adicionales import  Materia
from home.models.talento_humano import Usuario
from admisiones.models import Estudiantes
from django.contrib.auth.models import User
from home.models.talento_humano.usuarios import Usuario
class CategoriaEstudiante(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.nombre


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

class CategoriaDocente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.nombre


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

class CategoriaDirectivo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.nombre


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
    

from django.db import models
from admisiones.models import Estudiantes
from home.models.carga_academica.datos_adicionales import Materia

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
    respuestas = models.JSONField(
        help_text="Diccionario con claves de pregunta_id y valores con respuesta"
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.estudiante} en {self.materia} ({self.fecha_respuesta.date()})"

    class Meta:
        db_table = 'evaluacion_estudiante'
        verbose_name = 'Evaluación Estudiante'
        verbose_name_plural = 'Evaluaciones Estudiantes'
        unique_together = ('estudiante', 'materia')

from django.db import models
from django.contrib.auth.models import User


class EvaluacionDocente(models.Model):
    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    respuestas = models.JSONField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Autoevaluación de {self.docente}"

    @property
    def usuario(self):
        from home.models.talento_humano.usuarios import Usuario
        return Usuario.objects.filter(auth_user=self.docente).first()

    class Meta:
        db_table = 'evaluacion_docente'
        verbose_name = 'Evaluación Docente'
        verbose_name_plural = 'Evaluaciones Docentes'


class EvaluacionDirectivo(models.Model):
    evaluador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    docente_evaluado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='evaluaciones_directivos',
        limit_choices_to={'fk_rol__rol': 'D'}
    )
    respuestas = models.JSONField()  
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.docente_evaluado} por {self.evaluador}"

    class Meta:
        db_table = 'evaluacion_directivo'
        verbose_name = 'Evaluación Directivo'
        verbose_name_plural = 'Evaluaciones Directivos'