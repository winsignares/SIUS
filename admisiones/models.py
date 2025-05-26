from django.db import models
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia, Periodo
from home.models.talento_humano.tipo_documentos import TipoDocumento
from django.utils import timezone

# Create your models here.
class Estudiantes(models.Model):

    estudiante = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    fk_tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, default=0)
    numero_documento = models.BigIntegerField(unique=True, default=0)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, null=True, blank=True)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self):
        return f"{self.id} - {self.estudiante.username} - {self.programa.programa} - {self.semestre.descripcion}"
    
class Matricula(models.Model):
    estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)  # Campo nuevo
    fecha_matricula = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'materia', 'periodo')
        db_table = 'Matricula'
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
        Estudiantes,
        on_delete=models.CASCADE,
        
    )
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    fecha_aprobacion = models.DateField(default=timezone.now)
    estado_aprobacion = models.CharField(max_length=10, choices=ESTADO_OPCIONES)

    def __str__(self):
        return f"{self.estudiante} cursó {self.materia} - Estado: {self.estado_aprobacion}"

    class Meta:
        db_table = 'materia_cursada'
        unique_together = ('estudiante', 'materia')
        verbose_name = "Materia Cursada"
        verbose_name_plural = "Materias Cursadas"

