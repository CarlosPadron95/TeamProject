# 🚀 TeamProject: Collaborative Kanban Board with Role-Based Access Control

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 🌐 Local Demo

| | URL |
|---|---|
| 🖥️ **Servidor Local** | [http://127.0.0.1:8000](http://127.0.0.1:8000) |

---

### 🌍 Language / Idioma

[Versión en Español](#español) | [English Version](#english)

---

<a name="español"></a>
## Descripción (Español)

Aplicación web Full-Stack para la gestión colaborativa de proyectos con un tablero Kanban dinámico y un sistema granular de roles y permisos.

### 📋 Descripción

Esta aplicación permite:
- **Organizar** proyectos colaborativos asignando tareas con nivel de prioridad (Baja, Media, Alta), fechas límite y múltiples colaboradores simultáneos.
- **Gestionar Permisos de Roles**: Roles integrados (Administrador, Gestor, Desarrollador y Observador) que condicionan dinámicamente lo que el usuario puede ver y editar en la interfaz.
- **Interactuar con el Kanban**: Desplazar tareas entre las columnas fijas (*Por Hacer*, *En Progreso*, *Completado*) mediante arrastrar y soltar (Drag & Drop) restringido únicamente para los roles con permisos de edición (Admin y Manager).
- **Visualizar Estadísticas**: Gráfico de avance tipo dona (Chart.js) que mapea en colores semánticos (Rojo: Por Hacer, Amarillo: En Progreso, Verde: Completado) el progreso del proyecto en tiempo real.
- **Comunicarse en Equipo**: Muro interno de mensajes/chat rápido en cada proyecto.
- **Administrar Miembros**: Panel interactivo donde el Administrador del proyecto puede invitar nuevos colaboradores, removerlos o actualizar sus roles en vivo.

### ✨ Características
1. **Interfaz Premium Light Mode**: Estética moderna tipo SaaS, limpia, con degradados sutiles, sombras definidas y textos centrados en la cabecera.
2. **Seguridad y Roles**: Control de accesos tanto en el Frontend (interacciones de arrastre deshabilitadas o campos del formulario de tareas bloqueados para desarrolladores) como a nivel de Backend.
3. **Persistencia y Modularidad**: Base de datos relacional para persistir tareas, membresías, mensajes y orden del tablero.

### 🎯 Casos de Uso
- Coordinación ágil de equipos de desarrollo en proyectos compartidos.
- Gestión de flujos Kanban con roles diferenciados para responsables de producto y programadores.
- Demostración de control de acceso basado en roles (RBAC) y maquetación de componentes responsive.

---

<a name="english"></a>
## Description (English)

Full-Stack web application for collaborative project management featuring a dynamic Kanban board and a granular role-based access control system.

### 📋 Description

This application allows users to:
- **Organize** collaborative projects by assigning tasks with priority levels (Low, Medium, High), due dates, and multiple simultaneous assignees.
- **Manage Role-Based Permissions**: Built-in roles (Administrator, Manager, Developer, and Viewer) that dynamically control what each user can see and edit.
- **Interact with Kanban**: Move tasks between fixed columns (*To Do*, *In Progress*, *Completed*) via drag and drop (Drag & Drop) restricted only to authorized roles (Admin & Manager).
- **Visualize Progress**: A doughnut chart (Chart.js) mapping project progress in real-time using semantic colors (Red: To Do, Yellow: In Progress, Green: Completed).
- **Communicate in Real-Time**: Project discussion board/internal chat for team coordination.
- **Manage Members**: An interactive dashboard where the Project Administrator can invite new members, remove them, or update roles on the fly.

### ✨ Features
1. **Premium Light Mode Interface**: Modern SaaS dashboard aesthetics, clean layouts, subtle gradients, drop-shadows, and centered navbar branding.
2. **Security & Role Constraints**: Access controls enforced both in the Frontend (disabled dragging interactions and locked task fields for assigned developers) and verified on the Backend.
3. **Data Integrity**: Relational database schema to persist tasks, project memberships, board states, and internal discussions.

### 🎯 Use Cases
- Agile coordination of software development teams within shared workspaces.
- Kanban flow management with separated scopes for project managers and developer tasks.
- Demonstration of Role-Based Access Control (RBAC) and clean CSS component design.

---

## 👨‍💻 Autor / Author

**Carlos Padrón**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/CarlosPadron95)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/carlos-padr%C3%B3n-delgado-395166234/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:carlospadrondelgado@gmail.com)

⭐ Si te gustó este proyecto, dale una estrella / If you liked this project, give it a star!
