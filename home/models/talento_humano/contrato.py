from django.db import models
from .usuarios import Empleado
from .roles import Rol
from ..carga_academica.datos_adicionales import Periodo

# Create your models here.

class Dedicacion(models.Model):
    nombre_corto = models.CharField("Nombre Corto", max_length=10)
    nombre = models.CharField("Nombre Corto", max_length=100)
    class Meta:
        db_table = 'dedicacion'
        verbose_name = 'Dedicación'
        verbose_name_plural = 'Dedicaciones'

class TipoContrato(models.Model):
    tipo_contrato = models.CharField(verbose_name=('Tipo Contrato'), max_length=50, null=True, blank=True)
    descripcion = models.CharField(verbose_name=('Descripción'), max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'tipos_contrato'
        verbose_name = 'Tipo de Contrato'
        verbose_name_plural = 'Tipos de Contrato'


class Contrato(models.Model):
    id = models.AutoField(primary_key=True)
    fk_periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, verbose_name=("Periodo de contratación"), null=True, blank=True)
    fk_usuario = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="contrato", verbose_name=("Usuario"))
    fecha_inicio = models.DateField(verbose_name=('Fecha Inicio Contrato'), null=True, blank=True)
    fecha_fin = models.DateField(verbose_name=('Fecha Fin Contrato'), null=True, blank=True)
    fk_tipo_contrato = models.ForeignKey(TipoContrato, verbose_name=("Tipo Contrato"), on_delete=models.CASCADE, null=True, blank=True)
    fk_dedicacion = models.ForeignKey(Dedicacion, verbose_name=("Dedicación"), on_delete=models.CASCADE, null=True, blank=True)
    valor_contrato = models.IntegerField(verbose_name=('Valor del Contrato'), null=True, blank=True) # Solo para administrativos
    total_dias_laborados = models.IntegerField(verbose_name=('Total Dias Laborados'), null=True, blank=True)
    vigencia_contrato = models.BooleanField(verbose_name=('Vigencia del Contrato'), default=False)

    class Meta:
        db_table = 'contratos'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return f"{self.fk_usuario.primer_nombre} {self.fk_usuario.primer_apellido} | Inicio: {self.fecha_inicio} Fin: {self.fecha_fin}"


class DetalleContratro(models.Model):
    id = models.AutoField(primary_key=True)
    fk_contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name=("Contrato"))
    mes_a_pagar = models.CharField(verbose_name=('Mes a Pagar'), max_length=255, null=True, blank=True)
    dias_laborados = models.IntegerField(verbose_name=('Dias Laborados'), null=True, blank=True)
    valor_a_pagar = models.IntegerField(verbose_name=('Valor a Pagar'), null=True, blank=True)

    class Meta:
        db_table = 'detalles_contrato'
        verbose_name = 'Detalle de Contrato'
        verbose_name_plural = 'Detalles de Contrato'

    def __str__(self):
        return f"{self.fk_contrato.fk_usuario.primer_nombre} {self.fk_contrato.fk_usuario.primer_apellido}. Mes: {self.mes_a_pagar} - Total a Pagar: {self.valor_a_pagar}"