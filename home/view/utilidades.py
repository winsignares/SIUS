# Importar Librerías
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Exists, OuterRef

# Importar Modelos
from home.models import Empleado, EmpleadoUser, EstadoRevision, TipoDocumento, NivelAcademico, EPS, AFP, ARL, Departamento, CajaCompensacion, Institucion, Sede, Rol, Contrato, Dedicacion, CargaAcademica, Materia, Periodo, Programa, ProgramaUser, Semestre

def obtener_db_info(request, incluir_datos_adicionales=False):
    """
        Función auxiliar para obtener información especifica del usuario autenticado.
        Además, se incluye el envío de datos de la base de dato si alguna otra función lo requiere.
    """
    usuario_autenticado = request.user
    grupos_usuario = usuario_autenticado.groups.values_list('name', flat=True)

    # Obtener el empleado vinculado a este usuario (puede haber varios; tomamos el primero)
    try:
        empleado_user = EmpleadoUser.objects.select_related('fk_empleado').filter(fk_user=usuario_autenticado).first()
        if empleado_user:
            usuario_log = empleado_user.fk_empleado
            usuario_log.primer_nombre = usuario_log.primer_nombre.capitalize()
            usuario_log.primer_apellido = usuario_log.primer_apellido.capitalize()
            usuario_log.cargo = usuario_log.cargo.upper()
        else:
            usuario_log = None
    except EmpleadoUser.DoesNotExist:
        usuario_log = None

    # Obtener el programa del usuario logueado
    programa_usuario_log = ProgramaUser.objects.filter(fk_user=usuario_autenticado.id).first()
    programa_usuario = programa_usuario_log.fk_programa if programa_usuario_log else None

    # Obtener el número de semestres del programa
    num_semestres = int(programa_usuario.numero_semestres) if programa_usuario else 0

    # Filtrar los semestres hasta el número del programa
    semestres_list = Semestre.objects.filter(id__lte=num_semestres).order_by("id")

    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    periodo_actual = Periodo.objects.filter(fecha_apertura__lte=fecha_actual, fecha_cierre__gte=fecha_actual).first()

    programas = Programa.objects.all().values(
        'id',
        'codigo_snies',
        'programa',
        'nivel_formacion',
        'sede',
        'numero_semestres'
    )

    # Todas las materias
    materias_list_all = Materia.objects.all().values(
        'id',
        'materia',
        'codigo',
        'fk_semestre_id',
        'fk_programa_id'
    )

    # Se filtran las materias por el programa del usuario logueado
    materias_queryset = Materia.objects.select_related('fk_semestre').filter(
        fk_programa=programa_usuario).values(
            'id',
            'materia',
            'codigo',
            'horas_semanales',
            'fk_semestre_id'
        )

    # Obtener los docentes con contrato vigente en el periodo actual
    docentes = Empleado.objects.annotate(tiene_contrato=Exists(Contrato.objects.filter(fk_usuario=OuterRef('id'),fk_periodo_id=periodo_actual.id,vigencia_contrato=True))).filter(fk_rol_id__in=[2, 4],fk_estado_revision=1,activo=True,tiene_contrato=True).order_by('primer_nombre')
    docentes_con_dedicacion = []
    for docente in docentes:
        contrato = Contrato.objects.filter(fk_usuario=docente.id, fk_periodo_id=periodo_actual.id, vigencia_contrato=True).first()
        dedicacion_nombre_corto = contrato.fk_dedicacion.nombre_corto if contrato and contrato.fk_dedicacion else None
        # Crear un dict o puedes usar setattr en el objeto si quieres
        docente_dict = {
            'id': docente.id,
            'primer_nombre': docente.primer_nombre,
            'segundo_nombre': docente.segundo_nombre,
            'primer_apellido': docente.primer_apellido,
            'segundo_apellido': docente.segundo_apellido,
            'dedicacion': dedicacion_nombre_corto,
        }
        docentes_con_dedicacion.append(docente_dict)

    if programa_usuario and periodo_actual:
        cargas_academicas = CargaAcademica.objects.filter(
            fk_periodo_id=periodo_actual.id,
            fk_programa=programa_usuario.id
        ).order_by('id')
    else:
        cargas_academicas = CargaAcademica.objects.none()

    # Contexto inicial
    contexto = {
        'usuario_log': usuario_log,
        'user_groups': grupos_usuario,
        'programa_usuario': programa_usuario
    }

    # Incluir datos adicionales si es necesario para otras funciones
    if incluir_datos_adicionales:
        contexto.update({
            'tipos_documento_list': TipoDocumento.objects.all(),
            'departamentos_list': Departamento.objects.all(),
            'eps_list': EPS.objects.all().order_by('id'),
            'arl_list': ARL.objects.all(),
            'cajas_compensacion_list': CajaCompensacion.objects.all(),
            'afp_list': AFP.objects.all(),
            'niveles_academicos_list': NivelAcademico.objects.all(),
            'roles_list': Rol.objects.filter(id__in=[2, 3, 4]),
            'instituciones_list': Institucion.objects.all().order_by('codigo'),
            'sedes_list': Sede.objects.all(),
            'semestres_list': semestres_list,
            'programas_list': list(programas),
            'materias_list_all': list(materias_list_all),
            'materias_list': list(materias_queryset),
            'periodos_list': Periodo.objects.all(),
            'docentes_list': docentes_con_dedicacion,
            'cargas_academicas': cargas_academicas,
            'periodo_actual': periodo_actual,
            'dedicacion_list': Dedicacion.objects.all(),
            'estado_revision_list': EstadoRevision.objects.all()
        })

    return contexto


def error_404_view(request, exception):
    """
    Vista para manejar errores 404.
    """

    return render(request, '404.html', status=404)