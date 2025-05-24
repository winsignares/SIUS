from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group

from django.contrib import messages
from django.core.paginator import Paginator

from .views_home import obtener_db_info
from ..models import Estudiantes
from home.models.talento_humano.tipo_documentos import TipoDocumento
from home.models.carga_academica.datos_adicionales import Programa, Semestre

def gestion_estudiante(request, estudiante_id=None):
    estudiante = None

    if estudiante_id:
        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)

    estudiantes_list = Estudiantes.objects.all().order_by('id')
    paginator = Paginator(estudiantes_list, 5)
    page_number = request.GET.get('page')
    estudiantes = paginator.get_page(page_number)

    if request.method == 'POST':
        # Datos de usuario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Datos de Estudiantes
        tipo_documento_id = request.POST.get('fk_tipo_documento')
        numero_documento = request.POST.get('numero_documento')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        programa_id = request.POST.get('programa')
        semestre_id = request.POST.get('semestre')

        if estudiante:  # Editar estudiante existente
            estudiante.fk_tipo_documento_id = tipo_documento_id
            estudiante.numero_documento = numero_documento
            estudiante.fecha_nacimiento = fecha_nacimiento
            estudiante.programa_id = programa_id
            estudiante.semestre_id = semestre_id

            # Actualizar usuario
            user = estudiante.estudiante
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.password = f"{numero_documento}{last_name[0].lower()}{first_name[0].lower()}"
            user.save()

            estudiante.save()
            messages.success(request, 'Estudiante actualizado correctamente.')
        else:  # Crear estudiante y usuario
            username = f"{first_name.lower()}.{last_name.lower()}{numero_documento[-3:]}"
            password = f"{numero_documento}{last_name[0].lower()}{first_name[0].lower()}"

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )

            grupo, creado = Group.objects.get_or_create(name='Estudiante')
            user.groups.add(grupo)

            Estudiantes.objects.create(
                estudiante=user,
                fk_tipo_documento_id=tipo_documento_id,
                numero_documento=numero_documento,
                fecha_nacimiento=fecha_nacimiento,
                programa_id=programa_id,
                semestre_id=semestre_id
            )
            messages.success(request, 'Estudiante creado correctamente.')

        return redirect('gestion_estudiante')
    
    contexto = obtener_db_info(request)

    contexto.update({
        'estudiantes': estudiantes,
        'estudiante': estudiante,
        'tipos_documento': TipoDocumento.objects.all(),
        'programas': Programa.objects.all(),
        'semestres': Semestre.objects.all(),
    })   

    return render(request, 'core/estudiantes.html', contexto)


def eliminar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiantes, id=estudiante_id)
    if estudiante.estudiante:
        estudiante.estudiante.delete()  # Elimina el usuario también
        
        
    estudiante.delete()
    messages.success(request, 'Estudiante eliminado correctamente.')
    return redirect('gestion_estudiante')
