document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const content = document.querySelector('.content');
    const mesaOptions = document.querySelectorAll('.mesa-option');
    const eliminarBtns = document.querySelectorAll('.eliminar-btn');
    const asignarMesaBtn = document.getElementById('asignar-mesa-btn');
    const nuevaOrdenBtn = document.getElementById('nueva-orden-btn');
    const ordenContainer = document.querySelector('.orden-container');

    // Manejar el estado del menú lateral
    menuToggle.addEventListener('change', function() {
        if (this.checked) {
            sidebar.classList.add('expanded');
            content.classList.add('expanded');
        } else {
            sidebar.classList.remove('expanded');
            content.classList.remove('expanded');
        }
    });

    // Efecto hover para las mesas
    mesaOptions.forEach(option => {
        option.addEventListener('mouseenter', function() {
            this.querySelector('.mesa-box').style.transform = 'translateY(-3px)';
            this.querySelector('.mesa-box').style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        });

        option.addEventListener('mouseleave', function() {
            this.querySelector('.mesa-box').style.transform = '';
            this.querySelector('.mesa-box').style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
        });

        // Selección de mesa
        option.addEventListener('click', function() {
            mesaOptions.forEach(opt => {
                opt.querySelector('.mesa-box').classList.remove('selected');
            });
            this.querySelector('.mesa-box').classList.add('selected');
        });
    });

    // Eliminar órdenes
    eliminarBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const ordenId = this.getAttribute('data-orden-id');
            confirmarEliminacion(ordenId, this.closest('.orden-card'));
        });
    });

    // Asignar mesa
    asignarMesaBtn.addEventListener('click', function() {
        const mesaSeleccionada = document.querySelector('input[name="mesa-seleccionada"]:checked');
        if (mesaSeleccionada) {
            window.location.href = `/menu/?mesa=${mesaSeleccionada.value}`;
        } else {
            mostrarAlerta('Por favor selecciona una mesa primero');
        }
    });

    // Nueva orden
    nuevaOrdenBtn.addEventListener('click', function() {
        window.location.href = '/menu/';
    });

    // Funciones auxiliares
    function confirmarEliminacion(ordenId, ordenCard) {
        const modal = document.createElement('div');
        modal.className = 'confirm-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <p>¿Estás seguro de querer eliminar esta orden?</p>
                <div class="modal-buttons">
                    <button class="modal-btn confirm">Sí, eliminar</button>
                    <button class="modal-btn cancel">Cancelar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.confirm').addEventListener('click', function() {
            eliminarOrden(ordenId, ordenCard);
            modal.remove();
        });
        
        modal.querySelector('.cancel').addEventListener('click', function() {
            modal.remove();
        });
    }

    function eliminarOrden(ordenId, ordenCard) {
        fetch(`/api/ordenes/${ordenId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                ordenCard.remove();
                mostrarNotificacion('Orden eliminada correctamente', 'success');
                
                // Si no quedan órdenes, mostrar mensaje
                if (ordenContainer.querySelectorAll('.orden-card').length === 0) {
                    const noOrdenes = document.createElement('p');
                    noOrdenes.className = 'no-ordenes';
                    noOrdenes.textContent = 'No hay órdenes activas';
                    ordenContainer.appendChild(noOrdenes);
                }
            } else {
                throw new Error('Error al eliminar la orden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al eliminar la orden', 'error');
        });
    }

    function mostrarAlerta(mensaje) {
        const alerta = document.createElement('div');
        alerta.className = 'custom-alert';
        alerta.textContent = mensaje;
        document.body.appendChild(alerta);
        
        setTimeout(() => {
            alerta.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            alerta.classList.remove('show');
            setTimeout(() => {
                alerta.remove();
            }, 300);
        }, 3000);
    }

    function mostrarNotificacion(mensaje, tipo) {
        const notificacion = document.createElement('div');
        notificacion.className = `custom-notification ${tipo}`;
        notificacion.textContent = mensaje;
        document.body.appendChild(notificacion);
        
        setTimeout(() => {
            notificacion.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notificacion.classList.remove('show');
            setTimeout(() => {
                notificacion.remove();
            }, 300);
        }, 3000);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Estilos dinámicos para las notificaciones
    const style = document.createElement('style');
    style.textContent = `
        .confirm-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal-content {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 400px;
            width: 90%;
            text-align: center;
        }
        
        .modal-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .modal-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .modal-btn.confirm {
            background-color: var(--danger-color);
            color: white;
        }
        
        .modal-btn.cancel {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .custom-alert, .custom-notification {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 24px;
            border-radius: 4px;
            color: white;
            background-color: var(--secondary-color);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1000;
        }
        
        .custom-alert.show, .custom-notification.show {
            opacity: 1;
        }
        
        .custom-notification.success {
            background-color: var(--success-color);
        }
        
        .custom-notification.error {
            background-color: var(--danger-color);
        }
    `;
    document.head.appendChild(style);
});