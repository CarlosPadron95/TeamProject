import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Project, ProjectMember, Task, ProjectMessage, Column

# --- 1. FORMULARIO DE INICIO DE SESIÓN ---
# Se encarga de capturar el nombre de usuario y contraseña para entrar a la app.
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Recorremos todos los campos y les agregamos la clase de Bootstrap/CSS 'form-control'
        # para que se vean redondeados, con bordes suaves y elegantes.
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# --- 2. FORMULARIO DE REGISTRO DE USUARIOS ---
# Permite crear una nueva cuenta en la base de datos de la aplicación.
class CustomUserCreationForm(UserCreationForm):
    # Hacemos obligatorio el campo del correo electrónico
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cambiamos la etiqueta por defecto de Django a español amigable
        self.fields['username'].label = "Nombre de Usuario"
        # Limpiamos los textos de ayuda automáticos de Django (los de 'su contraseña no puede ser...')
        # para que no ensucien el diseño visual de la pantalla.
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.help_text = None

    # Validación personalizada para que las contraseñas sean seguras y cumplan requisitos
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            # Comprobamos la longitud mínima de la clave (mínimo 8 caracteres)
            if len(password) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
            # Comprobamos con una expresión regular que contenga al menos un número
            if not re.search(r'\d', password):
                raise forms.ValidationError("La contraseña debe contener al menos un número.")
        return password


# --- 3. FORMULARIO DE PROYECTO ---
# Se utiliza para crear un proyecto nuevo o modificar uno existente.
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # Solo necesitamos que el usuario ingrese el nombre y la descripción
        fields = ['name', 'description']
        # Definimos widgets personalizados con clases CSS y placeholders sugerentes
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. App de Reservas'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del proyecto...'}),
        }


# --- 4. FORMULARIO DE TAREA ---
# Permite crear tareas o editarlas en el tablero Kanban.
class TaskForm(forms.ModelForm):
    # Campo de fecha límite renderizado con un selector de fecha del navegador (type="date")
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Fecha Límite"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'column', 'priority', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Diseñar Base de Datos'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles de la tarea...'}),
            'column': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            # Usamos múltiples checkboxes para que el administrador pueda asignar la tarea a varios usuarios a la vez
            'assigned_to': forms.CheckboxSelectMultiple(),
        }

    # Sobrescribimos el constructor para filtrar los datos dinámicamente según el proyecto actual
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            # 1. Filtramos las columnas: Solo mostramos las que pertenecen a este proyecto específico
            self.fields['column'].queryset = Column.objects.filter(project=project)
            # 2. Filtramos asignados: Solo se puede asignar a usuarios que sean miembros del proyecto o al dueño (owner)
            member_ids = list(project.memberships.values_list('user_id', flat=True))
            valid_user_ids = [project.owner.id] + member_ids
            self.fields['assigned_to'].queryset = User.objects.filter(id__in=valid_user_ids)


# --- 5. FORMULARIO DE INVITACIÓN DE MIEMBROS ---
# Permite ingresar el nombre de usuario de una persona para agregarla como colaborador del proyecto.
class ProjectMemberForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. carlos95'})
    )

    class Meta:
        model = ProjectMember
        # Solo seleccionamos el rol inicial que tendrá el invitado (ej. Desarrollador)
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    # Comprobamos que el nombre de usuario escrito de verdad exista registrado en la base de datos
    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            # Intentamos buscar el usuario en la tabla de Django
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Si no existe, lanzamos un error que se mostrará en pantalla debajo del campo
            raise forms.ValidationError("El usuario no existe en el sistema.")
        return user

