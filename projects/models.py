from django.db import models
from django.contrib.auth.models import User

# --- 1. MODELO DE PROYECTO ---
# Este modelo representa un proyecto en la base de datos.
# Cada proyecto tiene un creador (dueño), un nombre, una descripción opcional y una fecha de creación.
class Project(models.Model):
    # Nombre del proyecto (máximo 150 caracteres)
    name = models.CharField(max_length=150, verbose_name="Nombre del Proyecto")
    
    # Campo de texto libre para detallar de qué trata el proyecto
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # El usuario de Django que creó el proyecto. Si el usuario se elimina, su proyecto también (on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects", verbose_name="Propietario")
    
    # Se guarda automáticamente el día y la hora exacta en la que se crea el proyecto
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        # Configuro que los proyectos se ordenen automáticamente del más nuevo al más viejo
        ordering = ['-created_at']

    # Devuelve el nombre del proyecto cuando se imprime el objeto (útil para el panel de administración de Django)
    def __str__(self):
        return self.name


# --- 2. MODELO DE COLUMNA DEL TABLERO KANBAN ---
# Representa cada columna estática del tablero de un proyecto.
# Por defecto se crean tres al inicio: "Por Hacer", "En Progreso" y "Completado".
class Column(models.Model):
    # Cada columna pertenece obligatoriamente a un proyecto
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="columns", verbose_name="Proyecto")
    
    # Nombre de la columna (ej. "Por Hacer")
    name = models.CharField(max_length=100, verbose_name="Nombre de Columna")
    
    # Un número entero para saber en qué orden mostrar la columna de izquierda a derecha (0, 1, 2...)
    position = models.IntegerField(default=0, verbose_name="Posición")

    class Meta:
        # Ordena las columnas de menor a mayor posición
        ordering = ['position']

    # Devuelve el nombre de la columna al imprimir el objeto
    def __str__(self):
        return self.name


# --- 3. MODELO DE MIEMBRO Y ROL ---
# Vincula un usuario con un proyecto y le asigna un rol de permisos (admin, manager, developer, viewer).
class ProjectMember(models.Model):
    # Defino la lista de roles disponibles y sus etiquetas legibles
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gestor de Proyecto'),
        ('developer', 'Desarrollador'),
        ('viewer', 'Observador'),
    ]
    
    # El proyecto al que se une el colaborador
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships", verbose_name="Proyecto")
    
    # El usuario colaborador
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_memberships", verbose_name="Usuario")
    
    # El rol que tiene (por defecto es desarrollador)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer', verbose_name="Rol")

    class Meta:
        # Regla de seguridad: Un usuario solo puede tener un único rol dentro del mismo proyecto
        unique_together = ('project', 'user')

    # Muestra el nombre del usuario junto a su rol y el proyecto al imprimir
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} en {self.project.name}"


# --- 4. MODELO DE TAREA ---
# Representa una tarea dentro de una de las columnas del tablero Kanban.
class Task(models.Model):
    # Opciones de prioridad para organizar la urgencia de las tareas
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]
    
    # La columna del Kanban a la que pertenece la tarea actualmente
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name="tasks", verbose_name="Columna")
    
    # Título o nombre de la tarea (máximo 200 caracteres)
    title = models.CharField(max_length=200, verbose_name="Título de la Tarea")
    
    # Detalles extensos sobre lo que se debe hacer en la tarea
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Nivel de prioridad, por defecto media
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Prioridad")
    
    # Relación de muchos a muchos: Varios usuarios pueden estar asignados a la misma tarea
    assigned_to = models.ManyToManyField(User, blank=True, related_name="assigned_tasks", verbose_name="Asignado a")
    
    # Fecha límite opcional para entregar la tarea
    due_date = models.DateField(null=True, blank=True, verbose_name="Fecha Límite")
    
    # Fecha de creación de la tarea, se guarda sola
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    
    # Posición para ordenar las tareas de forma vertical dentro de una misma columna
    position = models.IntegerField(default=0, verbose_name="Posición")

    class Meta:
        # Ordeno las tareas por su posición y luego por fecha de creación
        ordering = ['position', 'created_at']

    # Muestra el título de la tarea al imprimir el objeto
    def __str__(self):
        return self.title


# --- 5. MODELO DE MENSAJE INTERNO (CHAT DEL PROYECTO) ---
# Permite a los miembros comunicarse enviando mensajes en el muro del proyecto.
class ProjectMessage(models.Model):
    # El proyecto en cuyo muro se escribe el mensaje
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="messages", verbose_name="Proyecto")
    
    # Quién envía el mensaje
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", verbose_name="Remitente")
    
    # El contenido escrito del mensaje
    content = models.TextField(verbose_name="Mensaje")
    
    # Fecha y hora exactas del envío, se guarda de forma automática
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado el")

    class Meta:
        # Ordena los mensajes del más viejo al más nuevo para leer la conversación en orden correcto
        ordering = ['sent_at']

    # Representación en texto para identificar el mensaje fácilmente
    def __str__(self):
        return f"Mensaje de {self.sender.username} en {self.project.name}"
