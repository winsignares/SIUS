from django.db import models
from .roles import Rol
from .tipo_documentos import TipoDocumento
from .datos_adicionales import EPS, AFP, ARL, CajaCompensacion, Departamento, Sede, Pais
from .niveles_academicos import NivelAcademico
from django.conf import settings


class EstadoRevision(models.Model):
    estado = models.CharField(max_length=50)
    class Meta:
        db_table = 'estado_revision'
        verbose_name = 'Estado de Revisión'
        verbose_name_plural = 'Estados de Revisión'

    def __str__(self):
        return f"{self.estado}"

class Empleado(models.Model):
    # Campos obligatorios
    id = models.AutoField(primary_key=True)
    fk_rol = models.ForeignKey(Rol, on_delete=models.CASCADE) # ✅
    fk_tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE) # ✅
    cargo = models.CharField(max_length=255) # ✅
    primer_nombre = models.CharField(max_length=255) # ✅
    primer_apellido = models.CharField(max_length=255) # ✅
    numero_documento = models.BigIntegerField(unique=True) # ✅
    correo_personal = models.EmailField() # ✅
    fk_estado_revision = models.ForeignKey(EstadoRevision, on_delete=models.CASCADE, null=True, blank=True) # Pendiente - Rechazado - Aceptado

# Campos opcionales
    segundo_nombre = models.CharField(max_length=255, null=True, blank=True) # ✅
    segundo_apellido = models.CharField(max_length=255, null=True, blank=True) # ✅
    fecha_nacimiento = models.DateField(null=True, blank=True) # ✅
    fk_pais_nacimiento = models.ForeignKey(Pais, on_delete=models.CASCADE, null=True, blank=True) # ✅
    lugar_nacimiento = models.CharField(max_length=255, null=True, blank=True) # ✅
    fecha_expedicion_documento = models.DateField(null=True, blank=True) # ✅
    lugar_expedicion_documento = models.CharField(max_length=255, null=True, blank=True) # ✅
    sexo = models.CharField(max_length=50, null=True, blank=True) # ✅
    telefono_fijo = models.CharField(max_length=15, null=True, blank=True) # ✅
    celular = models.CharField(max_length=15, null=True, blank=True) # ✅
    estado_civil = models.CharField(max_length=255, null=True, blank=True) # ✅
    fk_ultimo_nivel_estudio = models.ForeignKey(NivelAcademico, on_delete=models.CASCADE, null=True, blank=True) # ✅
    fk_eps = models.ForeignKey(EPS, on_delete=models.CASCADE, null=True, blank=True) # ✅
    fk_arl = models.ForeignKey(ARL, on_delete=models.CASCADE, null=True, blank=True)
    fk_afp = models.ForeignKey(AFP, on_delete=models.CASCADE, null=True, blank=True) # ✅
    fk_caja_compensacion = models.ForeignKey(CajaCompensacion, on_delete=models.CASCADE, null=True, blank=True)
    direccion_residencia = models.CharField(max_length=255, null=True, blank=True) # ✅
    fk_departamento_residencia = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True, blank=True) # ✅
    ciudad_residencia = models.CharField(max_length=255, null=True, blank=True) # ✅
    barrio_residencia = models.CharField(max_length=255, null=True, blank=True) # ✅
    fk_sede_donde_labora = models.ForeignKey(Sede, on_delete=models.CASCADE, null=True, blank=True)
    url_hoja_de_vida = models.URLField(blank=True, null=True) # Enlace a Hoja de Vida
    activo = models.BooleanField(default=False) # True = Activo - False = Inactivo

    # Creación del usuario
    fk_creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='usuarios_creados', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Modificación del usuario
    fk_modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='usuarios_modificados', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


class EmpleadoUser(models.Model):

    fk_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='usuarios', verbose_name='Empleado')
    fk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empleados', verbose_name='User Asignado')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'empleado_user'
        verbose_name = "EmpleadoUser"
        verbose_name_plural = "EmpleadoUsers"
        unique_together = ('fk_empleado', 'fk_user')

    def __str__(self):
        return f'{self.fk_empleado.primer_nombre} {self.fk_empleado.primer_apellido} - {self.fk_user.username}'
