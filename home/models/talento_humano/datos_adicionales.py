from django.db import models


class departamentos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'departamentos'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return f"{self.nombre}"


class eps(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'eps'
        verbose_name = 'EPS'
        verbose_name_plural = 'EPS'

    def __str__(self):
        return f"{self.nombre}"


class arl(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'arl'
        verbose_name = 'ARL'
        verbose_name_plural = 'ARL'

    def __str__(self):
        return f"{self.nombre}"


class afp(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'afp'
        verbose_name = 'AFP'
        verbose_name_plural = 'AFP'

    def __str__(self):
        return f"{self.nombre}"


class cajas_compensacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'cajas_compensacion'
        verbose_name = 'Caja de compensacion'
        verbose_name_plural = 'Cajas de compensacion'

    def __str__(self):
        return f"{self.nombre}"
