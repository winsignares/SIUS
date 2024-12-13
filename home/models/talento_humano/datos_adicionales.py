from django.db import models


class Departamento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'departamentos'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return f"{self.nombre}"


class EPS(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'eps'
        verbose_name = 'EPS'
        verbose_name_plural = 'EPS'

    def __str__(self):
        return f"{self.nombre}"


class ARL(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'arl'
        verbose_name = 'ARL'
        verbose_name_plural = 'ARL'

    def __str__(self):
        return f"{self.nombre}"


class AFP(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'afp'
        verbose_name = 'AFP'
        verbose_name_plural = 'AFP'

    def __str__(self):
        return f"{self.nombre}"


class CajaCompensacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'cajas_compensacion'
        verbose_name = 'Caja de compensación'
        verbose_name_plural = 'Cajas de compensación'

    def __str__(self):
        return f"{self.nombre}"
