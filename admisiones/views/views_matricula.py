from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .views_home import obtener_db_info
from home.models.carga_academica.datos_adicionales import Programa, Semestre, Materia, Periodo
from django.contrib.auth.models import User
from ..models import Estudiantes, Matricula, Prerrequisito, MateriaAprobada
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.db.models import Q
@login_required
def seleccionar_programa_semestre(request):
    programas = Programa.objects.all()
    semestres = Semestre.objects.all()
    materias = None  
    estudiantes = []  

    programa_id = request.GET.get('programa')
    semestre_id = request.GET.get('semestre')

    if programa_id and semestre_id:
        
        materias = Materia.objects.filter(
            fk_programa_id=programa_id,
            fk_semestre_id=semestre_id
        )

        
        estudiantes = Estudiantes.objects.filter(
            programa_id=programa_id, 
              
        )

        for estudiante in estudiantes:
            try:
                user = User.objects.get(username=estudiante.estudiante)
                estudiante.nombre_completo = user.get_full_name()  
                estudiante.correo_personal = user.email  
            except User.DoesNotExist:
                estudiante.nombre_completo = "Usuario no encontrado"
                estudiante.correo_personal = "Correo no disponible"

    busqueda_realizada = bool(programa_id and semestre_id)
    contexto = obtener_db_info(request)
    contexto.update({
        'programas': programas,
        'semestres': semestres,
        'materias': materias,
        'estudiantes': estudiantes,
        'busqueda_realizada': busqueda_realizada,  
        'request': request  
    })

    return render(request, 'core/matricular_estudiantes.html', contexto)


@login_required
def buscar_estudiantes(request):
    query = request.GET.get('q', '').strip()
    programa_id = request.GET.get('programa', '').strip()

    if not programa_id:
        return JsonResponse({'error': 'Debe seleccionar un programa'}, status=400)

    estudiantes = Estudiantes.objects.select_related('estudiante').filter(programa_id=programa_id)

    if query:
        estudiantes = estudiantes.filter(
            Q(numero_documento__icontains=query) |
            Q(estudiante__first_name__icontains=query) |
            Q(estudiante__last_name__icontains=query)
        )

    resultado = []
    for est in estudiantes:
        user = est.estudiante
        if user:
            resultado.append({
                'id': est.id,
                'nombre_completo': f"{user.first_name} {user.last_name}",
                'numero_documento': est.numero_documento,
                'semestre':str(est.semestre),
                'correo': user.email,
            })

    return JsonResponse({'estudiantes': resultado})

@login_required
def validar_codigo(request):
    codigo = request.GET.get('numero_documento')
    valido = Estudiantes.objects.filter(numero_documento=codigo).exists()
    return JsonResponse({'valido': valido})

@login_required
def matricular_estudiante(request):
    if request.method == 'POST':
        identificacion = request.POST.get('numero_documento')
        materias_ids = request.POST.getlist('materias')

        if not identificacion:
            messages.error(request, 'Código de estudiante no proporcionado.')
            return redirect('seleccionar_programa_semestre')

        try:
            estudiante = Estudiantes.objects.get(numero_documento=identificacion)
        except Estudiantes.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado o no tiene rol de estudiante.')
            return redirect('seleccionar_programa_semestre')

        if not estudiante.programa or not estudiante.semestre:
            messages.error(request, 'El estudiante no tiene asignado un programa o semestre.')
            return redirect('seleccionar_programa_semestre')

        periodo_activo = Periodo.objects.filter(
            fecha_apertura__lte=timezone.now(),
            fecha_cierre__gte=timezone.now()
        ).first()

        if not periodo_activo:
            messages.error(request, 'No hay un periodo activo para matricular.')
            return redirect('seleccionar_programa_semestre')

        materias_a_matricular = []
        errores = []
        materias_matriculadas = Matricula.objects.filter(
            estudiante=estudiante,
            periodo=periodo_activo
        ).values_list('materia_id', flat=True)

        for materia_id in materias_ids:
            try:
                materia = Materia.objects.get(id=materia_id)

                if materia.id in materias_matriculadas:
                    errores.append(f'Ya está matriculado en {materia.materia} para el periodo activo.')
                    continue

                prerrequisitos = Prerrequisito.objects.filter(materia=materia)
                prerrequisito_no_aprobado = False

                for prerrequisito in prerrequisitos:
                    if not MateriaAprobada.objects.filter(
                        estudiante=estudiante,
                        materia=prerrequisito.prerequisito,
                        estado_aprobacion='aprobada'
                    ).exists():
                        errores.append(
                            f'No cumple con el prerrequisito "{prerrequisito.prerequisito.materia}" para la materia "{materia.materia}".'
                        )
                        prerrequisito_no_aprobado = True
                        break

                if prerrequisito_no_aprobado:
                    continue

                materias_a_matricular.append(materia)

            except Materia.DoesNotExist:
                errores.append(f'La materia con ID {materia_id} no existe.')

        for error in errores:
            messages.warning(request, error)

        if materias_a_matricular:
            for materia in materias_a_matricular:
                Matricula.objects.create(
                    estudiante=estudiante,
                    materia=materia,
                    periodo=periodo_activo
                )
            messages.success(request, f'Matrícula completada con éxito para {len(materias_a_matricular)} materias.')
        elif not materias_a_matricular:
            messages.error(request, 'No se pudo completar la matrícula. Verifique las materias seleccionadas.')

        return redirect('seleccionar_programa_semestre')

    messages.error(request, 'Método no permitido.')
    return redirect('seleccionar_programa_semestre')

@login_required
def validar_materias(request):
    codigo = request.GET.get('codigo')
    try:
        estudiante = Estudiantes.objects.get(codigo_estudiante=codigo, fk_rol__rol='E')
    except Estudiantes.DoesNotExist:
        return JsonResponse({'error': 'Estudiante no encontrado.'}, status=400)

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=timezone.now(),
        fecha_cierre__gte=timezone.now()
    ).first()

    if not periodo_activo:
        return JsonResponse({'error': 'No hay periodo activo.'}, status=400)

    materias_inscritas = list(Matricula.objects.filter(
        estudiante=estudiante,
        periodo=periodo_activo
    ).values_list('materia_id', flat=True))
    return JsonResponse({'materias_inscritas': materias_inscritas}, status=200)

@login_required
def estudiantes_inscritos(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=timezone.now(),
        fecha_cierre__gte=timezone.now()
    ).first()

    matriculas = Matricula.objects.filter(
        materia=materia,
        periodo=periodo_activo
    ).select_related('estudiante')

    estudiantes = [matricula.estudiante for matricula in matriculas]

    for estudiante in estudiantes:
        try:
            user = User.objects.get(username=estudiante.estudiante)
            estudiante.nombre_completo = user.get_full_name()
            estudiante.correo_personal = user.email
        except User.DoesNotExist:
            estudiante.nombre_completo = "Usuario no encontrado"
            estudiante.correo_personal = "Correo no disponible"

    context = obtener_db_info(request)
    context.update({
        'materia': materia,
        'estudiantes': estudiantes,
        'request': request
    })

    return render(request, 'core/listado_estudiantes_inscritos.html', context)

@login_required
def eliminar_estudiante(request, materia_id, estudiante_id):
    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)
        materia = get_object_or_404(Materia, id=materia_id)
        
        periodo_activo = Periodo.objects.filter(
            fecha_apertura__lte=timezone.now(),
            fecha_cierre__gte=timezone.now()
        ).first()

        matricula = get_object_or_404(
            Matricula,
            estudiante=estudiante,
            materia=materia,
            periodo=periodo_activo
        )
        matricula.delete()
        
        messages.success(request, f"El estudiante con identificación: {estudiante.numero_documento}, fue eliminado de la materia {materia.materia}.")
        return redirect('estudiantes_inscritos', materia_id=materia.id)
    
    return redirect('estudiantes_inscritos', materia_id=materia_id)



@login_required
def materias_matriculadas_por_estudiante(request):
    numero_documento = request.GET.get('numero_documento')

    if not numero_documento:
        return JsonResponse({"error": "Número de documento no proporcionado."}, status=400)

    try:
        estudiante = Estudiantes.objects.select_related('programa').get(numero_documento=numero_documento)
    except Estudiantes.DoesNotExist:
        return JsonResponse({"error": "Estudiante no encontrado."}, status=404)

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=timezone.now(),
        fecha_cierre__gte=timezone.now()
    ).first()

    if not periodo_activo:
        return JsonResponse({
            "materias_excluir": [],
            "mensajes_rechazo": {},
            "info": "No hay periodo activo"
        }, status=200)

   
    materias_matriculadas_ids = set(Matricula.objects.filter(
        estudiante=estudiante,
        periodo=periodo_activo
    ).values_list('materia_id', flat=True))

   
    materias_cursadas_qs = MateriaAprobada.objects.filter(estudiante=estudiante)
    materias_cursadas_ids = set(materias_cursadas_qs.values_list('materia_id', flat=True))
    materias_aprobadas_ids = set(materias_cursadas_qs.filter(
        estado_aprobacion='aprobada'
    ).values_list('materia_id', flat=True))

    materias_prerrequisito_no_aprobado = set()
    mensajes_rechazo = {}

    
    materias = Materia.objects.filter(
        fk_programa=estudiante.programa
    ).prefetch_related(
        Prefetch('materia_principal', queryset=Prerrequisito.objects.select_related('prerequisito'))
    )

    for materia in materias:
        for prereq in materia.materia_principal.all():
            if prereq.prerequisito_id not in materias_aprobadas_ids:
                materias_prerrequisito_no_aprobado.add(materia.id)
                mensajes_rechazo[materia.id] = (
                    f"No puedes matricular '{materia.materia}' porque no has aprobado "
                    f"su prerrequisito: '{prereq.prerequisito.materia}'."
                )
                break  

    materias_excluir = materias_matriculadas_ids.union(
        materias_cursadas_ids,
        materias_prerrequisito_no_aprobado
    )

    return JsonResponse({
        "materias_excluir": list(materias_excluir),
        "mensajes_rechazo": mensajes_rechazo
    })