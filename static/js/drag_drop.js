document.addEventListener('DOMContentLoaded', () => {
    // Buscamos todas las tarjetas de tarea que tengan activada la opción de arrastre (draggable="true")
    // Recuerda: solo a los administradores y gestores les renderizamos draggable="true" en el HTML
    const cards = document.querySelectorAll('.task-card[draggable="true"]');
    // Buscamos las zonas donde podemos soltar las tareas (las listas de cada columna)
    const lists = document.querySelectorAll('.kanban-tasks-list');

    // 1. EVENTOS DE ARRASTRE PARA LAS TARJETAS (CARDS)
    cards.forEach(card => {
        // Se ejecuta cuando el usuario empieza a arrastrar la tarjeta con el ratón
        card.addEventListener('dragstart', (e) => {
            // Guardamos el ID de la tarea dentro del portapapeles del arrastre para recuperarlo después
            e.dataTransfer.setData('text/plain', card.getAttribute('data-task-id'));
            // Agregamos una clase de CSS para darle un efecto semitransparente mientras se arrastra
            card.classList.add('dragging');
        });

        // Se ejecuta cuando el usuario suelta la tarjeta (sea donde sea)
        card.addEventListener('dragend', () => {
            // Quitamos el efecto semitransparente para que vuelva a su color original
            card.classList.remove('dragging');
        });
    });

    // 2. EVENTOS PARA LAS ZONAS DE DESTINO (COLUMNAS KANBAN)
    lists.forEach(list => {
        // Se ejecuta repetidamente cuando tenemos la tarjeta arrastrada sobre esta columna
        list.addEventListener('dragover', (e) => {
            // Obligatorio para permitir soltar elementos en la web
            e.preventDefault();
            // Añadimos una clase para resaltar visualmente con borde o fondo que podemos soltar aquí
            list.classList.add('drag-over');
        });

        // Se ejecuta cuando arrastramos la tarjeta fuera de la columna sin haberla soltado
        list.addEventListener('dragleave', () => {
            // Quitamos el resaltado visual
            list.classList.remove('drag-over');
        });

        // Se ejecuta cuando soltamos finalmente la tarjeta dentro de esta columna
        list.addEventListener('drop', async (e) => {
            e.preventDefault();
            // Quitamos el resaltado visual de la columna
            list.classList.remove('drag-over');
            
            // Recuperamos el ID de la tarea que habíamos guardado en el evento dragstart
            const taskId = e.dataTransfer.getData('text/plain');
            // Obtenemos el ID de la columna destino desde sus atributos HTML
            const columnId = list.getAttribute('data-column-id');
            // Buscamos el elemento visual de la tarjeta en la página
            const cardElement = document.querySelector(`.task-card[data-task-id="${taskId}"]`);

            if (cardElement && columnId) {
                // Paso A: Movemos la tarjeta visualmente en el navegador metiéndola en la nueva lista
                list.appendChild(cardElement);

                // Paso B: Mandamos la información a Django en segundo plano usando Fetch (petición AJAX)
                try {
                    const response = await fetch('/api/task/move/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            // Enviamos el token de seguridad CSRF obligatorio para evitar que Django rechace la petición
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            task_id: taskId,
                            column_id: columnId
                        })
                    });

                    const result = await response.json();
                    if (result.status === 'success') {
                        // Si Django guardó el cambio con éxito, recargamos la página
                        // Esto actualiza el gráfico circular de avance de tareas en la parte superior
                        window.location.reload();
                    } else {
                        // Si el backend responde con un error de permisos o base de datos, mostramos el aviso
                        alert(result.message || 'Error al mover la tarea.');
                        // Recargamos para devolver la tarjeta a su columna original
                        window.location.reload();
                    }
                } catch (error) {
                    console.error('Error al mover tarea:', error);
                    alert('Error en el servidor al procesar el arrastre.');
                    window.location.reload();
                }
            }
        });
    });
});

// --- FUNCIÓN UTILITARIA: OBTENER COOKIES ---
// Django exige enviar un token CSRF (seguridad contra falsificación de peticiones) en las cabeceras POST.
// Esta función lee las cookies del navegador para buscar la cookie llamada 'csrftoken'.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Comprobamos si esta cookie empieza con el nombre que buscamos seguido de "="
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

