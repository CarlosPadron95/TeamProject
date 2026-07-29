from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, forms

urlpatterns = [
    # --- 1. RUTAS DE ACCESO Y SEGURIDAD (AUTENTICACIÓN) ---
    # Registro de nuevos usuarios
    path('register/', views.register_view, name='register'),
    
    # Login personalizado (inyecto el formulario estilizado CustomAuthenticationForm)
    path('login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        authentication_form=forms.CustomAuthenticationForm
    ), name='login'),
    
    # Cierre de sesión de la app
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- 2. RUTAS DE PROYECTOS (DASHBOARD Y EDICIÓN) ---
    # Dashboard principal con la lista de proyectos en los que participa el usuario
    path('', views.project_list_view, name='project_list'),
    
    # Formulario para crear un nuevo proyecto
    path('project/new/', views.project_create_view, name='project_create'),
    
    # El tablero Kanban y foro interno de un proyecto en particular
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    
    # Formulario para editar nombre/descripción del proyecto
    path('project/<int:project_id>/edit/', views.project_edit_view, name='project_edit'),
    
    # Confirmación de borrado definitivo del proyecto
    path('project/<int:project_id>/delete/', views.project_delete_view, name='project_delete'),

    # --- 3. RUTAS DE COLABORADORES Y EQUIPO ---
    # Panel de visualización y administración de miembros del proyecto
    path('project/<int:project_id>/members/', views.project_members_view, name='project_members'),
    
    # Endpoint rápido para cambiar el rol de un colaborador desde el selector dropdown
    path('project/<int:project_id>/members/role/<int:member_id>/', views.update_member_role_view, name='update_member_role'),
    
    # Enlace para remover definitivamente a un colaborador del equipo
    path('project/<int:project_id>/members/remove/<int:member_id>/', views.remove_member_view, name='remove_member'),

    # --- 4. RUTAS DE TAREAS (CRUD KANBAN) ---
    # Formulario para crear una tarea nueva en este proyecto
    path('project/<int:project_id>/task/new/', views.task_create_view, name='task_create'),
    
    # Formulario para editar campos o mover la tarea de columna
    path('task/<int:task_id>/edit/', views.task_edit_view, name='task_edit'),
    
    # Confirmación de eliminación de una tarea
    path('task/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),

    # --- 5. ENDPOINTS DE API (AJAX / JAVASCRIPT) ---
    # Ruta que recibe las peticiones Fetch de JavaScript para mover tareas al arrastrarlas
    path('api/task/move/', views.update_task_column_api, name='api_move_task'),
]

