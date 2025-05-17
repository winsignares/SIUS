from django.db import models

class CategoriaEstudiante(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

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
    descripcion = models.TextField(blank=True, null=True)

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
    descripcion = models.TextField(blank=True, null=True)

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
