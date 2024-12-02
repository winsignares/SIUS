from django.contrib import admin
from .models import TipoDocumento, Rol, Usuario
# Register your models here.

admin.site.register(TipoDocumento)
admin.site.register(Rol)
admin.site.register(Usuario)