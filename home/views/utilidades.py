# Importar Librerías
from collections import defaultdict
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Exists, OuterRef

# Importar Modelos
from home.models import Empleado, EmpleadoUser, EstadoRevision, TipoDocumento, NivelAcademico, EPS, AFP, ARL, Departamento, CajaCompensacion, Institucion, Sede, Rol, Contrato, Dedicacion, CargaAcademica, Materia, Periodo, Programa, ProgramaUser, Semestre, NivelAcademicoHistorico


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
    ).order_by('programa')

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
        ).order_by('codigo')

    # Obtener los docentes con contrato vigente en el periodo actual
    docentes = Empleado.objects.annotate(tiene_contrato=Exists(Contrato.objects.filter(fk_usuario=OuterRef('id'),fk_periodo_id=periodo_actual.id,vigencia_contrato=True))).filter(fk_rol_id__in=[2, 4, 8],fk_estado_revision=1,activo=True,tiene_contrato=True).order_by('primer_nombre')
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

    rol_docente = Rol.objects.filter(id__in=[2, 4, 8])
    roles_docentes = list(rol_docente.values_list('id', flat=True))

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
            'roles_list': Rol.objects.filter(id__in=[2, 3, 4, 8]),
            'roles_docentes': roles_docentes,
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


def calcular_dias_laborados_por_contrato(fecha_inicio, fecha_final):
    """
    Calcula los días laborados durante todo el contrato, considerando meses de 30 días.
    """
    fecha_inicio = datetime.strptime(str(fecha_inicio), "%Y-%m-%d")
    fecha_final = datetime.strptime(str(fecha_final), "%Y-%m-%d")

    # Calcular meses completos y días restantes
    meses = (fecha_final.year - fecha_inicio.year) * 12 + (fecha_final.month - fecha_inicio.month)
    dias = fecha_final.day - fecha_inicio.day + 1

    if dias < 0:
        meses -= 1
        dias += 30  # Siempre sumamos 30 días, no los reales del mes

    dias_laborados = meses * 30 + dias
    return dias_laborados if dias_laborados > 0 else 0


def calcular_dias_laborados_por_mes(fecha_inicio, fecha_final):
    """
    Calcula los días laborados en cada mes del contrato, con un máximo de 30 días por mes.
    """
    dias_laborados_por_mes = defaultdict(int)
    current = fecha_inicio

    while current <= fecha_final:
        key = (current.year, current.month)
        dias_laborados_por_mes[key] += 1
        current += timedelta(days=1)

    return dias_laborados_por_mes


def calcular_valor_a_pagar(total_horas, id_docente):
    """
    Calcula el valor a pagar según las horas semanales y el total de horas, además de la dedicación del docente.
    """
    fk_ultimo_nivel_estudio = Empleado.objects.get(id=id_docente).fk_ultimo_nivel_estudio
    tarifa_base = NivelAcademicoHistorico.objects.filter(fk_nivel_academico=fk_ultimo_nivel_estudio).order_by('-año_vigencia').first()
    if not tarifa_base:
        raise Exception("No existe tarifa base para el nivel académico del docente.")
    valor_a_pagar = total_horas * tarifa_base.tarifa_base_por_hora
    return valor_a_pagar


def contar_meses_completos(fecha_inicio, fecha_fin):
    if fecha_fin < fecha_inicio:
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    # Ajustar al inicio y fin de mes
    fecha_inicio = fecha_inicio.replace(day=1)
    fecha_fin = fecha_fin.replace(day=1)

    diferencia = relativedelta(fecha_fin, fecha_inicio)
    meses = diferencia.years * 12 + diferencia.months + 1

    return meses


def nombre_mes(mes):
    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }
    return meses.get(mes, "Mes inválido")


def no_autorizado(request):
    return render(request, "no_autorizado.html")