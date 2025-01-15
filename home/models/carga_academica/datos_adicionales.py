from django.db import models

class Programa(models.Model):
    id = models.AutoField(primary_key=True)
    programa = models.CharField(max_length=255, null= True, blank= True)
    codigo = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'programas'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return f"{self.codigo} - {self.programa}"


class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    fk_programa = models.ForeignKey(Programa, on_delete=models.CASCADE)
    materia = models.CharField(max_length=255, null= True, blank= True)
    codigo = models.CharField(max_length=255, unique=True)
    credito = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return f" {self.codigo} - {self.materia}"