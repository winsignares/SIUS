from django.urls import path
from home import views

urlpatterns = [

    # LOGIN
    path('login/',views.iniciar_sesion_form, name="iniciar_sesion_form"),
    path('login/validacion/',views.signin, name="signin"),

    # CAMBIAR CONTRASEÑA
    path('reset_psw/',views.restablecer_contraseña_form, name="restablecer_contraseña_form"),
    path('reset_psw/update/',views.actualizar_contraseña, name="actualizar_contraseña"),

    # PÁGINA PRINCIPAL
    path('dashboard/home/', views.dashboard, name='dashboard'),

    # CERRAR SESIÓN - PRUEBA
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),

    # MÓDULO DE ASPIRANTES (VISTA Y FORMULARIO DE AGREGAR ASPIRANTE)
    path("dashboard/aspirantes/", views.gestion_aspirantes, name="gestion_aspirantes"),
    path("dashboard/aspirantes/agregar_aspirante/", views.agregar_aspirante, name="agregar_aspirante"),

    # MÓDULO DE EMPLEADOS (VISTA Y FORMULARIO DE AGREGAR EMPLEADO)
    path("dashboard/empleados/", views.gestion_empleados, name="gestion_empleados"),
    path("dashboard/aspirantes/agregar_empleado/", views.agregar_empleado, name="agregar_empleado"),

    # FORMULARIOS PARA AGREGAR INFORMACIÓN ACADÉMICA A LOS USUARIOS AGREGADOS (EMPLEADOS Y ASPIRTANTES)
    path("dashboard/aspirantes/agregar_exp_laboral/", views.agregar_exp_laboral, name="agregar_exp_laboral"),
    path("dashboard/aspirantes/agregar_detalle_academico/", views.agregar_detalle_academico, name="agregar_detalle_academico"),

    # MÓDULO DE CONTRATOS
    path("dashboard/docentes/", views.gestion_contratos_docentes, name="gestion_contratos_docentes"),
    path("dashboard/docentes/contratos/", views.contratos_docentes, name="contratos_docentes"),
    path('dashboard/docentes/aprobaciones/aprobar_contrato_contabilidad/', views.aprobar_contrato_contabilidad, name='aprobar_contrato_contabilidad'),
    path("dashboard/docentes/aprobaciones/aprobar_contratos_contabilidad/", views.aprobar_contratos_contabilidad, name="aprobar_contratos_contabilidad"),
    path('dashboard/docentes/aprobaciones/aprobar_contrato_rectoria/', views.aprobar_contrato_rectoria, name='aprobar_contrato_rectoria'),
    path("dashboard/docentes/aprobaciones/aprobar_contratos_rectoria/", views.aprobar_contratos_rectoria, name="aprobar_contratos_rectoria"),
    path('dashboard/docentes/aprobaciones/aprobar_contrato_presidencia/', views.aprobar_contrato_presidencia, name='aprobar_contrato_presidencia'),
    path("dashboard/docentes/generar_contrato_pdf/<int:contrato_id>/", views.ver_contrato_docente_pdf, name="ver_contrato_docente_pdf"),
    path("dashboard/docentes/detalles_contrato/<int:contrato_id>/", views.detalles_contrato_docente, name="detalles_contrato_docente"),

    path("dashboard/administrativos/", views.gestion_contratos_administrativos, name="gestion_contratos_administrativos"),

    # MÓDULO DE REPORTES
    path("dashboard/reportes/", views.reportes, name="reportes"),

    # OPERACIONES DE LOS GRUPOS "SECRETARIA TALENTO HUMANO" Y "DIRECTOR TALENTO HUMANO"
    path('dashboard/usuario/detalle_usuario/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path("dashboard/usuario/editar_usuario/<str:tipo>/<int:usuario_id>/", views.editar_usuario, name="editar_usuario"),
    path("dashboard/usuario/guardar_usuario/<int:usuario_id>/", views.actualizar_usuario, name="actualizar_usuario"),
    path("dashboard/usuario/definir_contrato/<int:usuario_id>/", views.definir_contrato, name="definir_contrato"),
    path("dashboard/usuario/definir_contrato_usuario/<int:usuario_id>/", views.definir_contrato_usuario, name="definir_contrato_usuario"),

    # MÓDULO DE CARGA ACADÉMICA
    path("dashboard/carga_academica/", views.gestion_carga_academica, name="gestion_carga_academica"),
    path("dashboard/carga_academica/aprobaciones/", views.gestion_cargas_aprobaciones, name="gestion_cargas_aprobaciones"),
    path("dashboard/carga_academica/aprobaciones/filtrar_cargas_academicas/", views.filtrar_cargas_academicas, name="filtrar_cargas_academicas"),
    path('dashboard/carga_academica/aprobaciones/aprobar_carga_academica_vicerrectoria/', views.aprobar_carga_academica_vicerrectoria, name='aprobar_carga_academica_vicerrectoria'),
    path("dashboard/carga_academica/aprobaciones/aprobar_cargas_academicas_vicerrectoria/", views.aprobar_cargas_academicas_vicerrectoria, name="aprobar_cargas_academicas_vicerrectoria"),

    # MÓDULO DE MATRIZ DE CARGA ACADÉMICA
    path("dashboard/matriz/", views.gestion_matriz, name="gestion_matriz"),
    path("dashboard/matriz/guardar_matriz/", views.guardar_matriz, name="guardar_matriz"),

    # MÓDULO DE FUNCIONES SUSTANTIVAS
    path("dashboard/funciones_sustantivas/", views.gestion_func_sustantivas, name="gestion_func_sustantivas"),

    # MÓDULO DE NO AUTORIZADO
    path("dashboard/home/no_autorizado/", views.no_autorizado, name="no_autorizado"),
]
