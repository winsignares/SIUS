from django.db import models
from home.models.carga_academica.datos_adicionales import  Materia
from home.models.talento_humano import Usuario
from admisiones.models import Estudiantes
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
    

#zona de prueba

class EvaluacionEstudiante(models.Model):
    estudiante = models.ForeignKey(
        Estudiantes,
        on_delete=models.CASCADE,
        
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE
    )
    pregunta = models.ForeignKey(
        PreguntaEstudiante,
        on_delete=models.CASCADE
    )
    respuesta = models.PositiveSmallIntegerField()  
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta de {self.estudiante} en {self.materia}: {self.pregunta} -> {self.respuesta}"

    class Meta:
        db_table = 'evaluacion_estudiante'
        verbose_name = 'Evaluación Estudiante'
        verbose_name_plural = 'Evaluaciones Estudiantes'

class EvaluacionDocente(models.Model):
    docente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'fk_rol__rol': 'D'}
    )
    pregunta = models.ForeignKey(
        PreguntaDocente,
        on_delete=models.CASCADE
    )
    respuesta = models.PositiveSmallIntegerField()  
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Autoevaluación de {self.docente}: {self.pregunta} -> {self.respuesta}"

    class Meta:
        db_table = 'evaluacion_docente'
        verbose_name = 'Evaluación Docente'
        verbose_name_plural = 'Evaluaciones Docentes'


class EvaluacionDirectivo(models.Model):
    directivo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'fk_rol__rol': 'DR'}
    )
    docente_evaluado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='evaluaciones_directivos',
        limit_choices_to={'fk_rol__rol': 'D'}
    )
    pregunta = models.ForeignKey(
        PreguntaDirectivo,
        on_delete=models.CASCADE
    )
    respuesta = models.PositiveSmallIntegerField()  
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.docente_evaluado} por {self.directivo}: {self.pregunta} -> {self.respuesta}"

    class Meta:
        db_table = 'evaluacion_directivo'
        verbose_name = 'Evaluación Directivo'
        verbose_name_plural = 'Evaluaciones Directivos'