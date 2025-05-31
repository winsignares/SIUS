from home.models.carga_academica.datos_adicionales  import Programa, Semestre, Materia, Periodo
from django.contrib.auth.models import User
from django.utils import timezone

from home.models.talento_humano.usuarios import EmpleadoUser

def obtener_db_info(request, incluir_datos_adicionales=False):
    """
        Función auxiliar para obtener información especifica del usuario autenticado.
        Además, se incluye el envío de datos de la base de dato si alguna otra función lo requiere.
    """
    usuario_autenticado = request.user    
    grupos_usuario = usuario_autenticado.groups.values_list('name', flat=True)

    try:
        usuario_log = User.objects.get(username=usuario_autenticado)
        usuario_log.primer_nombre = usuario_log.first_name.capitalize()
        usuario_log.primer_apellido = usuario_log.last_name.capitalize()
        usuario_log.cargo = usuario_log.groups.first().name.upper()

        if usuario_log.cargo != 'ESTUDIANTE':
            empleado_user = EmpleadoUser.objects.select_related('fk_empleado').filter(fk_user=usuario_autenticado).first()
            if empleado_user:
                usuario_log = empleado_user.fk_empleado
                usuario_log.primer_nombre = usuario_log.primer_nombre.capitalize()
                usuario_log.primer_apellido = usuario_log.primer_apellido.capitalize()
                usuario_log.cargo = usuario_log.cargo.upper()
                print(usuario_log)
                
    except User.DoesNotExist:
        usuario_log = None

    # Contexto inicial
    contexto = {
        'usuario_log': usuario_log,
        'user_groups': grupos_usuario,
    }

    # Incluir datos adicionales si es necesario para otras funciones
    if incluir_datos_adicionales:
        # Obtener el programa del usuario logueado (Almacenado en first_name)
        programa_usuario = Programa.objects.filter(programa=usuario_autenticado.first_name).first()

        # Obtener el número de semestres del programa
        num_semestres = int(programa_usuario.numero_semestres) if programa_usuario else 0

        # Filtrar los semestres hasta el número del programa
        semestres_list = Semestre.objects.filter(id__lte=num_semestres).order_by("id")

        # Obtener la fecha actual
        fecha_actual = timezone.now().date()

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
                'horas',
                'fk_semestre_id'
            )

        contexto.update({            
            'semestres_list': semestres_list,
            'programas_list': list(programas),
            'materias_list_all': list(materias_list_all),
            'materias_list': list(materias_queryset),
            'periodos_list': Periodo.objects.all(),
            'docentes_list': User.objects.filter(fk_rol_id=4, estado_revision='Pendiente'),
            'periodo_actual': Periodo.objects.filter(fecha_apertura__lte=fecha_actual, fecha_cierre__gte=fecha_actual).first()
        })

    return contexto