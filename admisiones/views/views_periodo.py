from django.shortcuts import render, redirect, get_object_or_404
from home.models.carga_academica.datos_adicionales import Periodo
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def gestion_periodo(request, periodo_id=None):
    if periodo_id:
        periodo_editar = get_object_or_404(Periodo, id=periodo_id)
    else:
        periodo_editar = None

    if request.method == 'POST':
        year = request.POST.get('year')
        periodo = request.POST.get('periodo')
        fecha_apertura = request.POST.get('fecha_apertura') or None
        fecha_cierre = request.POST.get('fecha_cierre') or None
        salario_minimo = request.POST.get('salario_minimo') or None
        auxilio_transporte = request.POST.get('auxilio_transporte') or None

        
        if not year:
            messages.error(request, 'El campo Año es obligatorio.')
            return redirect('gestion_periodo')

        if periodo_editar:
            periodo_editar.year = year
            periodo_editar.periodo = periodo
            periodo_editar.fecha_apertura = fecha_apertura
            periodo_editar.fecha_cierre = fecha_cierre
            periodo_editar.salario_minimo = salario_minimo or None
            periodo_editar.auxilio_transporte = auxilio_transporte or None
            periodo_editar.save()
            messages.success(request, 'Periodo actualizado correctamente.')
            return redirect('gestion_periodo')
        else:
            if Periodo.objects.filter(year=year).exists():
                messages.error(request, 'Ya existe un periodo con ese año.')
            else:
                Periodo.objects.create(
                    year=year,
                    periodo=periodo,
                    fecha_apertura=fecha_apertura,
                    fecha_cierre=fecha_cierre,
                    salario_minimo=salario_minimo or None,
                    auxilio_transporte=auxilio_transporte or None
                )
                messages.success(request, 'Periodo creado correctamente.')
            return redirect('gestion_periodo')

    periodos = Periodo.objects.all().order_by('-id')
    return render(request, 'core/periodo.html', {
        'periodos': periodos,
        'periodo_editar': periodo_editar
    })

@login_required
def eliminar_periodo(request, periodo_id):
    periodo = get_object_or_404(Periodo, id=periodo_id)
    periodo.delete()
    messages.success(request, 'Periodo eliminado correctamente.')
    return redirect('gestion_periodo')
