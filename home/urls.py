from django.urls import path
from home import views
from home import view

urlpatterns = [

    # # LOGIN
    path('login/',view.iniciar_sesion_form, name="iniciar_sesion_form"),
    path('login/validacion/',view.signin, name="signin"),

    # # CAMBIAR CONTRASEÑA
    path('reset_psw/',view.restablecer_contraseña_form, name="restablecer_contraseña_form"),
    path('reset_psw/update/',view.actualizar_contraseña, name="actualizar_contraseña"),

    # # PÁGINA PRINCIPAL
    path('dashboard/home/', view.dashboard, name='dashboard'),

    # CERRAR SESIÓN - PRUEBA
    path('logout/', view.cerrar_sesion, name='cerrar_sesion'),

    # # MÓDULO DE ASPIRANTES (VISTA Y FORMULARIO DE AGREGAR ASPIRANTE)
    path("dashboard/aspirantes/", view.gestion_aspirantes, name="gestion_aspirantes"),
    path("dashboard/aspirantes/agregar_aspirante/", view.agregar_aspirante, name="agregar_aspirante"),

    # # MÓDULO DE EMPLEADOS (VISTA Y FORMULARIO DE AGREGAR EMPLEADO)
    path("dashboard/empleados/", view.gestion_empleados, name="gestion_empleados"),
    path("dashboard/aspirantes/agregar_empleado/", view.agregar_empleado, name="agregar_empleado"),

    # # FORMULARIOS PARA AGREGAR INFORMACIÓN ACADÉMICA A LOS USUARIOS AGREGADOS (EMPLEADOS Y ASPIRTANTES)
    path("dashboard/aspirantes/agregar_exp_laboral/", view.agregar_exp_laboral, name="agregar_exp_laboral"),
    path("dashboard/aspirantes/agregar_detalle_academico/", view.agregar_detalle_academico, name="agregar_detalle_academico"),

    # # MÓDULO DE CONTRATOS (CONTABILIDAD)
    path("dashboard/contratos/docentes/", view.gestion_contratos_docentes, name="gestion_contratos_docentes"),
    path("dashboard/contratos/administrativos/", view.gestion_contratos_administrativos, name="gestion_contratos_administrativos"),

    # # MÓDULO DE REPORTES
    path("dashboard/reportes/", view.reportes, name="reportes"),

    # # OPERACIONES DE LOS GRUPOS "SECRETARIA TALENTO HUMANO" Y "DIRECTOR TALENTO HUMANO"
    path('dashboard/detalle_usuario/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'), # Falta Corregir
    path("dashboard/editar_usuario/<str:tipo>/<int:usuario_id>/", views.editar_usuario, name="editar_usuario"), # Falta Corregir
    path("dashboard/guardar_usuario/<str:tipo>/<int:usuario_id>/", views.actualizar_usuario, name="actualizar_usuario"), # Falta Corregir
    path("dashboard/definir_contrato/<int:usuario_id>/", views.definir_contrato, name="definir_contrato"),
    path("dashboard/definir_contrato_usuario/<int:usuario_id>/", views.definir_contrato_usuario, name="definir_contrato_usuario"), # Falta Corregir

    # # MÓDULO DE CARGA ACADÉMICA
    path("dashboard/carga_academica/", views.gestion_carga_academica, name="gestion_carga_academica"), # Falta Corregir

    # # MÓDULO DE MATRIZ DE CARGA ACADÉMICA
    path("dashboard/matriz/", views.gestion_matriz, name="gestion_matriz"), # Falta Corregir
    path("dashboard/matriz/agregar_matriz_academica/", views.agregar_matriz_academica, name="agregar_matriz_academica"), # Falta Corregir

    # # MÓDULO DE FUNCIONES SUSTANTIVAS
    path("dashboard/funciones_sustantivas/", views.gestion_func_sustantivas, name="gestion_func_sustantivas"), # Falta Corregir
]
