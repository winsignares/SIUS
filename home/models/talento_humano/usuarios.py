from django.db import models
from .roles import Rol
from .tipo_documentos import TipoDocumento
from django.conf import settings


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    fk_rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    fk_tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=255)
    primer_nombre = models.CharField(max_length=255)
    segundo_nombre = models.CharField(max_length=255, null=True, blank=True)
    primer_apellido = models.CharField(max_length=255)
    segundo_apellido = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    lugar_nacimiento = models.CharField(max_length=255, null=True, blank=True)
    numero_documento = models.BigIntegerField(unique=True)
    fecha_expedicion_documento = models.DateField(null=True, blank=True)
    lugar_expedicion_documento = models.CharField(max_length=255, null=True, blank=True)
    sexo = models.CharField(max_length=50)
    telefono_fijo = models.CharField(max_length=15, null=True, blank=True)
    celular = models.CharField(max_length=15)
    correo_personal = models.EmailField()
    estado_civil = models.CharField(max_length=255, null=True, blank=True)
    ultimo_nivel_estudio = models.CharField(max_length=255, null=True, blank=True)
    eps = models.CharField(max_length=255)
    arl = models.CharField(max_length=255)
    afp = models.CharField(max_length=255)
    caja_compensacion = models.CharField(max_length=255)
    direccion_residencia = models.CharField(max_length=255)
    departamento_residencia = models.CharField(max_length=255)
    ciudad_residencia = models.CharField(max_length=255)
    barrio_residencia = models.CharField(max_length=255, null=True, blank=True)
    url_hoja_de_vida = models.URLField(blank=True, null=True) # Enlace a Hoja de Vida
    estado_revision = models.CharField(max_length=50) # Pendiente - Rechazado - Aceptado
    activo = models.BooleanField(default=True) # True = Activo - False = Inactivo
    fk_creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='usuarios_creados', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fk_modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='usuarios_modificados', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario_app') # Relación con auth_user para definir si el usuario puede iniciar sesión en el aplicativo

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"
