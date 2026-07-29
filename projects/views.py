import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q

from .models import Project, Column, ProjectMember, Task, ProjectMessage
from .forms import CustomUserCreationForm, ProjectForm, TaskForm, ProjectMemberForm

# --- FUNCIÓN AUXILIAR PARA OBTENER EL ROL ---
# Esta función nos ayuda a saber qué rol tiene un usuario en un proyecto específico.
# Si el usuario es el dueño original, le damos rol de 'admin'.
# Si no es el dueño, buscamos en la tabla de miembros (ProjectMember) qué rol tiene asignado.
# Si no pertenece al proyecto, devolvemos None.
def get_user_role(project, user):
    if project.owner == user:
        return 'admin'
    try:
        membership = ProjectMember.objects.get(project=project, user=user)
        return membership.role
    except ProjectMember.DoesNotExist:
        return None


# --- 1. REGISTRO DE USUARIOS ---
# Vista para crear una cuenta nueva. Si el usuario ya inició sesión, lo mandamos al listado.
def register_view(request):
    if request.user.is_authenticated:
        return redirect('project_list')
        
    if request.method == 'POST':
        # Procesamos los datos enviados por el usuario
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Guardamos el nuevo usuario e iniciamos sesión automáticamente
            user = form.save()
            login(request, user)
            return redirect('project_list')
    else:
        # Mostramos el formulario vacío
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


# --- 2. LISTADO DE PROYECTOS (DASHBOARD GENERAL) ---
# Muestra todos los proyectos en los que participa el usuario (ya sea como creador o colaborador).
@login_required
def project_list_view(request):
    # Buscamos proyectos donde el usuario sea dueño o aparezca en la lista de colaboradores
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(memberships__user=request.user)
    ).distinct()
    return render(request, 'projects/project_list.html', {'projects': projects})


# --- 3. CREAR PROYECTO (CON COLUMNAS POR DEFECTO) ---
# Vista para crear un proyecto nuevo y configurar automáticamente el equipo y tablero inicial.
@login_required
def project_create_view(request):
    role_choices = ProjectMember.ROLE_CHOICES

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Creamos el proyecto pero no lo guardamos en la BD todavía
            project = form.save(commit=False)
            # Asignamos al creador como dueño del proyecto
            project.owner = request.user
            project.save()
            
            # 1. Asignamos al creador como miembro Administrador (rol principal)
            ProjectMember.objects.create(project=project, user=request.user, role='admin')
            
            # 2. Asignamos los colaboradores iniciales agregados dinámicamente desde el buscador
            member_usernames = request.POST.getlist('member_usernames')
            member_roles = request.POST.getlist('member_roles')
            
            for username, role in zip(member_usernames, member_roles):
                clean_username = username.strip()
                if clean_username and clean_username.lower() != request.user.username.lower():
                    try:
                        invited_user = User.objects.get(username__iexact=clean_username)
                        valid_role = role if role in [r[0] for r in role_choices] else 'developer'
                        ProjectMember.objects.get_or_create(
                            project=project,
                            user=invited_user,
                            defaults={'role': valid_role}
                        )
                    except User.DoesNotExist:
                        continue
            
            # 3. Creamos las 3 columnas obligatorias por defecto de nuestro tablero Kanban
            Column.objects.create(project=project, name='Por Hacer', position=1)
            Column.objects.create(project=project, name='En Progreso', position=2)
            Column.objects.create(project=project, name='Completado', position=3)
            
            # Redirigimos al usuario al tablero del proyecto recién creado
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Nuevo Proyecto',
        'role_choices': role_choices,
        'current_username': request.user.username,
    })


# --- 4. DETALLE DE PROYECTO (TABLERO KANBAN Y CHAT) ---
# Esta es la vista principal que dibuja el tablero Kanban, carga el gráfico de Chart.js y gestiona el muro.
@login_required
def project_detail_view(request, project_id):
    # Obtenemos el proyecto o devolvemos un error 404 si no existe
    project = get_object_or_404(Project, id=project_id)
    
    # Comprobamos el rol del usuario actual
    role = get_user_role(project, request.user)
    if not role:
        return HttpResponseForbidden("No tienes acceso a este proyecto.")

    # Obtenemos todas las columnas y los mensajes del chat del proyecto
    columns = project.columns.all()
    messages = project.messages.all()

    # Preparamos las etiquetas y cantidades de tareas por columna para pintar la gráfica
    chart_labels = []
    chart_counts = []
    for col in columns:
        chart_labels.append(col.name)
        chart_counts.append(col.tasks.count())

    chart_data = {
        'labels': chart_labels,
        'counts': chart_counts,
        'total': sum(chart_counts)
    }

    # Lógica para enviar mensajes en el foro interno (permitido para todos excepto Viewers)
    if request.method == 'POST' and role != 'viewer':
        content = request.POST.get('content')
        if content:
            ProjectMessage.objects.create(project=project, sender=request.user, content=content)
            return redirect('project_detail', project_id=project.id)

    # Renderizamos la plantilla pasando los datos del proyecto, roles, columnas y el json de la gráfica
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'role': role,
        'columns': columns,
        'messages': messages,
        'chart_data_json': json.dumps(chart_data)
    })


# --- 5. EDITAR PROYECTO ---
# Permite modificar el nombre y descripción del proyecto (Solo disponible para Administradores).
@login_required
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    role = get_user_role(project, request.user)
    
    # Comprobación de seguridad: Solo admin puede pasar por aquí
    if role != 'admin':
        return HttpResponseForbidden("Solo los administradores pueden editar el proyecto.")

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Editar Proyecto', 'project': project})


# --- 6. ELIMINAR PROYECTO ---
# Elimina por completo el proyecto (Solo el creador/dueño puede hacerlo).
@login_required
def project_delete_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return HttpResponseForbidden("Solo el creador del proyecto puede eliminarlo.")

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})


# --- 7. GESTIÓN DE COLABORADORES Y ROLES (PÁGINA DE MIEMBROS) ---
# Muestra el equipo de trabajo. Permite invitar y reasignar roles si eres administrador.
@login_required
def project_members_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    role = get_user_role(project, request.user)
    
    # Seguridad básica: Debes ser miembro del proyecto para ver a los compañeros
    if not role:
        return HttpResponseForbidden("No tienes acceso a este proyecto.")

    memberships = project.memberships.all()

    # Si se envía el formulario para añadir un nuevo miembro
    if request.method == 'POST':
        if role != 'admin':
            return HttpResponseForbidden("Solo los administradores pueden gestionar miembros.")
            
        form = ProjectMemberForm(request.POST, project=project)
        if form.is_valid():
            user = form.cleaned_data.get('username')
            role_assigned = form.cleaned_data.get('role')
            # Creamos la membresía o la actualizamos si el usuario ya tenía un rol asignado
            ProjectMember.objects.update_or_create(
                project=project, user=user,
                defaults={'role': role_assigned}
            )
            return redirect('project_members', project_id=project.id)
    else:
        form = ProjectMemberForm(project=project)

    return render(request, 'projects/project_members.html', {
        'project': project,
        'memberships': memberships,
        'form': form,
        'role': role
    })


# --- 8. ACTUALIZAR ROL DE COLABORADOR (RÁPIDO) ---
# Cambia el rol de un miembro del equipo al seleccionar una opción del dropdown (Solo Administrador).
@login_required
def update_member_role_view(request, project_id, member_id):
    project = get_object_or_404(Project, id=project_id)
    role = get_user_role(project, request.user)
    
    if role != 'admin':
        return HttpResponseForbidden("Solo los administradores pueden cambiar roles.")

    member = get_object_or_404(ProjectMember, id=member_id, project=project)
    
    # Impedimos que el administrador se modifique o degrade su propio rol de creador
    if member.user == project.owner:
        return HttpResponseForbidden("No puedes cambiar el rol del propietario del proyecto.")

    if request.method == 'POST':
        new_role = request.POST.get('role')
        # Validamos que el rol esté dentro de las opciones válidas definidas en el modelo
        if new_role in dict(ProjectMember.ROLE_CHOICES):
            member.role = new_role
            member.save()

    return redirect('project_members', project_id=project.id)


# --- 9. ELIMINAR COLABORADOR ---
# Elimina a un colaborador del proyecto (Solo Administrador).
@login_required
def remove_member_view(request, project_id, member_id):
    project = get_object_or_404(Project, id=project_id)
    role = get_user_role(project, request.user)
    
    if role != 'admin':
        return HttpResponseForbidden("Solo los administradores pueden gestionar miembros.")

    member = get_object_or_404(ProjectMember, id=member_id, project=project)
    if member.user == project.owner:
        return HttpResponseForbidden("No puedes eliminar al propietario del proyecto.")

    member.delete()
    return redirect('project_members', project_id=project.id)


# --- 10. API PARA ACTUALIZAR COLUMNA (DRAG & DROP) ---
# Esta vista procesa la petición Fetch de Javascript cuando se arrastra una tarea.
@login_required
def update_task_column_api(request):
    if request.method == 'POST':
        try:
            # Parseamos el JSON recibido desde el cuerpo de la petición
            data = json.loads(request.body)
            task_id = data.get('task_id')
            column_id = data.get('column_id')

            task = get_object_or_404(Task, id=task_id)
            project = task.column.project
            role = get_user_role(project, request.user)

            # Seguridad: Solo admin, manager y desarrollador asignado pueden cambiar tareas de columna con Drag & Drop
            is_developer_assigned = (role == 'developer' and request.user in task.assigned_to.all())
            if role not in ['admin', 'manager'] and not is_developer_assigned:
                return JsonResponse({'status': 'error', 'message': 'No tienes permisos para arrastrar tareas.'}, status=403)

            # Obtenemos la columna destino del mismo proyecto y reasignamos la tarea
            target_column = get_object_or_404(Column, id=column_id, project=project)
            task.column = target_column
            task.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Método no soportado.'}, status=405)


# --- 11. CREAR TAREA ---
# Añade una nueva tarea a una columna del tablero (Disponible para Admin y Manager).
@login_required
def task_create_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    role = get_user_role(project, request.user)
    
    if role not in ['admin', 'manager']:
        return HttpResponseForbidden("No tienes permisos para añadir tareas.")

    if request.method == 'POST':
        # Le pasamos el proyecto al formulario para que filtre asignados y columnas
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            form.save_m2m()  # Guarda los colaboradores asignados (relación Many-to-Many)
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(project=project)
    return render(request, 'projects/task_form.html', {'form': form, 'title': 'Nueva Tarea', 'project': project})


# --- 12. EDITAR TAREA ---
# Permite modificar una tarea. Contiene restricciones dinámicas de campos según el rol.
@login_required
def task_edit_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.column.project
    role = get_user_role(project, request.user)

    # El Observador (viewer) o usuarios externos no pueden editar nada
    if not role or role == 'viewer':
        return HttpResponseForbidden("No tienes permisos para editar esta tarea.")

    # Comprobamos si el usuario es un desarrollador (developer) asignado a esta tarea específica
    is_developer_assigned = (role == 'developer' and request.user in task.assigned_to.all())

    # Si no es admin, ni manager, ni el desarrollador asignado, denegamos el acceso
    if role not in ['admin', 'manager'] and not is_developer_assigned:
        return HttpResponseForbidden("No puedes editar esta tarea.")

    if request.method == 'POST':
        if is_developer_assigned:
            # Lógica para Desarrolladores asignados: Solo pueden cambiar el estado/columna de la tarea
            new_column_id = request.POST.get('column')
            new_column = get_object_or_404(Column, id=new_column_id, project=project)
            task.column = new_column
            task.save()
            return redirect('project_detail', project_id=project.id)
        else:
            # Admin y Manager guardan el formulario completo con todos sus campos
            form = TaskForm(request.POST, instance=task, project=project)
            if form.is_valid():
                form.save()
                return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm(instance=task, project=project)
        if is_developer_assigned:
            # Deshabilitamos en el formulario de desarrolladores todos los campos excepto el de columna
            for field_name in ['title', 'description', 'priority', 'assigned_to', 'due_date']:
                if field_name in form.fields:
                    form.fields[field_name].disabled = True

    return render(request, 'projects/task_form.html', {
        'form': form,
        'title': 'Editar Tarea',
        'project': project,
        'task': task,
        'is_developer_assigned': is_developer_assigned
    })


# --- 13. ELIMINAR TAREA ---
# Elimina de forma definitiva una tarea (Disponible para Admin y Manager).
@login_required
def task_delete_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.column.project
    role = get_user_role(project, request.user)
    
    if role not in ['admin', 'manager']:
        return HttpResponseForbidden("No tienes permisos para eliminar tareas.")

    if request.method == 'POST':
        task.delete()
        return redirect('project_detail', project_id=project.id)
    return render(request, 'projects/task_confirm_delete.html', {'task': task, 'project': project})
