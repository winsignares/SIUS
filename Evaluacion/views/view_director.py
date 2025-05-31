from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Evaluacion.views.info_db import obtener_db_info
from ..models import CategoriaDirectivo, EvaluacionDirectivo
from home.models.talento_humano.usuarios import Empleado
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from home.models.carga_academica.datos_adicionales import Periodo, ProgramaUser, Materia
from django.utils.timezone import now
from home.models.carga_academica.carga_academica import CargaAcademica

@login_required
def listado_docentes(request):
    usuario_actual = ProgramaUser.objects.filter(fk_user=request.user).first()
    contexto = obtener_db_info(request)

    if not usuario_actual:
        mensaje_error = "No se encontró información asociada a tu cuenta. Contacta al administrador."
        return render(request, 'core/listado_docentes.html', {'mensaje_error': mensaje_error})

    if not usuario_actual.fk_programa:
        mensaje_error = "No tienes un programa asignado. Por favor, contacta a la administración."
        return render(request, 'core/listado_docentes.html', {'mensaje_error': mensaje_error})

    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    if not periodo_activo:
        mensaje_error = "No hay un periodo activo configurado. Contacta al administrador."
        contexto.update({'mensaje_error': mensaje_error})
        return render(request, 'core/listado_docentes.html', contexto)

    
    cargas = CargaAcademica.objects.filter(fk_programa=usuario_actual.fk_programa).select_related('fk_docente_asignado')

    docentes = []
    for carga in cargas:
        if carga.fk_docente_asignado:
            docente = carga.fk_docente_asignado
            docentes.append(docente)

    if not docentes:
        mensaje_advertencia = "No hay docentes disponibles con carga académica en tu programa."
        contexto.update({'mensaje_advertencia': mensaje_advertencia})
        return render(request, 'core/listado_docentes.html', contexto)

    
    docentes_unicos = list({docente.id: docente for docente in docentes}.values())

    
    paginator = Paginator(docentes_unicos, 7)
    page = request.GET.get('page')

    try:
        docentes_paginados = paginator.page(page)
    except PageNotAnInteger:
        docentes_paginados = paginator.page(1)
    except EmptyPage:
        docentes_paginados = paginator.page(paginator.num_pages)

   
    contexto.update({
        'docentes': docentes_paginados,
        'periodo': periodo_activo
    })

    return render(request, 'core/listado_docentes.html', contexto)



@login_required
def evaluar_docente(request, docente_id):
    # Obtener información del docente evaluado
    docente_evaluado = get_object_or_404(Empleado, id=docente_id)
    evaluador = request.user

    # Verificar el periodo activo
    periodo_activo = Periodo.objects.filter(
        fecha_apertura__lte=now(),
        fecha_cierre__gte=now()
    ).first()

    if not periodo_activo:
        messages.error(request, "No hay un periodo activo configurado. Contacta al administrador.")
        return redirect('evaluacion:listado_docentes')

    # Obtener categorías y preguntas asociadas
    categorias = CategoriaDirectivo.objects.prefetch_related('preguntas').all()
    preguntas_por_categoria = {
        categoria: categoria.preguntas.filter(activo=True)
        for categoria in categorias
    }

    # Verificar si ya existe una evaluación realizada para este periodo
    evaluacion_existente = EvaluacionDirectivo.objects.filter(
        evaluador=evaluador,
        docente_evaluado=docente_evaluado,
        periodo=periodo_activo
    ).first()

    if request.method == 'POST':
        if evaluacion_existente:
            messages.warning(request, "Ya realizaste esta evaluación para el periodo activo.")
            return redirect('evaluacion:listado_docentes')

        # Procesar las respuestas enviadas en el formulario
        respuestas = {}
        for categoria, preguntas in preguntas_por_categoria.items():
            for pregunta in preguntas:
                respuesta = request.POST.get(f'respuesta_{pregunta.id}')
                if respuesta is not None:
                    respuestas[str(pregunta.id)] = int(respuesta)

        if not respuestas:
            messages.error(request, "No se registraron evaluaciones.")
            return redirect('evaluacion:listado_docentes')

       
        EvaluacionDirectivo.objects.create(
            evaluador=evaluador,
            docente_evaluado=docente_evaluado,
            periodo=periodo_activo,
            respuestas=respuestas
        )

        messages.success(request, f"Evaluación registrada correctamente para el docente {docente_evaluado.primer_apellido}.")
        return redirect('evaluacion:listado_docentes')

    
    context = {
        'docente': docente_evaluado,
        'preguntas_por_categoria': preguntas_por_categoria,
        'evaluacion_existente': evaluacion_existente,
        'periodo': periodo_activo
    }
    return render(request, 'core/evaluar_docente.html', context)
