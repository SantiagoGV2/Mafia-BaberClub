// Verificar sesión
function verificarSesion() {
    const barberoId = sessionStorage.getItem('barberoId');
    if (!barberoId) {
        window.location.href = 'login.html';
        return;
    }
}

// Verificar sesión al cargar la página
verificarSesion();

// Datos de ejemplo (en un caso real, esto vendría de la base de datos)
const reservas = [
    {
        id: 1,
        cliente: "Juan Pérez",
        servicio: "Corte Clásico",
        hora_inicio: "10:00",
        hora_fin: "10:45",
        estado: "confirmada",
        duracion_estimada: 45,
        notas: "Cliente regular, prefiere fade"
    },
    {
        id: 2,
        cliente: "María García",
        servicio: "Tratamiento Capilar",
        hora_inicio: "11:00",
        hora_fin: "12:00",
        estado: "pendiente",
        duracion_estimada: 60,
        notas: "Primera visita"
    }
];

// Función para cargar las reservas
function cargarReservas(filtros = {}) {
    const container = document.getElementById('reservasContainer');
    container.innerHTML = '';

    let reservasFiltradas = reservas;

    if (filtros.fecha) {
        // Filtrar por fecha
    }

    if (filtros.estado && filtros.estado !== 'todos') {
        reservasFiltradas = reservasFiltradas.filter(r => r.estado === filtros.estado);
    }

    reservasFiltradas.forEach(reserva => {
        const card = crearReservaCard(reserva);
        container.appendChild(card);
    });
}

// Función para crear una tarjeta de reserva
function crearReservaCard(reserva) {
    const card = document.createElement('div');
    card.className = 'reservation-card p-3';
    card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
                <h5 class="mb-1">${reserva.cliente}</h5>
                <p class="text-muted mb-0">${reserva.servicio}</p>
            </div>
            <span class="reservation-status status-${reserva.estado}">${reserva.estado.toUpperCase()}</span>
        </div>
        <div class="row mb-3">
            <div class="col-md-6">
                <p class="mb-1"><i class="bi bi-clock me-2"></i> ${reserva.hora_inicio} - ${reserva.hora_fin}</p>
                <p class="mb-0"><i class="bi bi-hourglass me-2"></i> Duración estimada: ${reserva.duracion_estimada} min</p>
            </div>
            <div class="col-md-6">
                <p class="mb-1"><i class="bi bi-chat me-2"></i> Notas:</p>
                <p class="mb-0">${reserva.notas}</p>
            </div>
        </div>
        <div class="action-buttons">
            ${reserva.estado === 'confirmada' ? `
                <button class="btn btn-success btn-sm" onclick="iniciarServicio(${reserva.id})">
                    <i class="bi bi-play-fill me-1"></i> Iniciar
                </button>
            ` : ''}
            ${reserva.estado === 'en_progreso' ? `
                <button class="btn btn-primary btn-sm" onclick="completarServicio(${reserva.id})">
                    <i class="bi bi-check-lg me-1"></i> Completar
                </button>
            ` : ''}
            ${reserva.estado === 'pendiente' ? `
                <button class="btn btn-primary btn-sm" onclick="confirmarReserva(${reserva.id})">
                    <i class="bi bi-check-lg me-1"></i> Confirmar
                </button>
                <button class="btn btn-danger btn-sm" onclick="cancelarReserva(${reserva.id})">
                    <i class="bi bi-x-lg me-1"></i> Cancelar
                </button>
            ` : ''}
        </div>
        <div id="completionForm-${reserva.id}" class="completion-form">
            <div class="mb-3">
                <label class="form-label">Tiempo real de duración (minutos)</label>
                <input type="number" class="form-control" id="tiempoReal-${reserva.id}" min="1" max="120">
            </div>
            <div class="mb-3">
                <label class="form-label">Notas adicionales</label>
                <textarea class="form-control" id="notasAdicionales-${reserva.id}" rows="2"></textarea>
            </div>
            <button class="btn btn-success btn-sm" onclick="guardarCompletado(${reserva.id})">
                <i class="bi bi-save me-1"></i> Guardar
            </button>
        </div>
    `;
    return card;
}

// Función para iniciar un servicio
function iniciarServicio(reservaId) {
    const reserva = reservas.find(r => r.id === reservaId);
    if (reserva) {
        reserva.estado = 'en_progreso';
        cargarReservas();
    }
}

// Función para completar un servicio
function completarServicio(reservaId) {
    const form = document.getElementById(`completionForm-${reservaId}`);
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// Función para guardar el completado de un servicio
function guardarCompletado(reservaId) {
    const tiempoReal = document.getElementById(`tiempoReal-${reservaId}`).value;
    const notasAdicionales = document.getElementById(`notasAdicionales-${reservaId}`).value;
    
    const reserva = reservas.find(r => r.id === reservaId);
    if (reserva) {
        reserva.estado = 'completada';
        reserva.tiempo_real = parseInt(tiempoReal);
        reserva.notas_adicionales = notasAdicionales;
        
        // Si el servicio se completó antes de tiempo, enviar notificación
        if (reserva.tiempo_real < reserva.duracion_estimada) {
            enviarNotificacionActualizacion(reserva);
        }
        
        cargarReservas();
    }
}

// Función para enviar notificación de actualización
function enviarNotificacionActualizacion(reserva) {
    console.log(`Notificación enviada a ${reserva.cliente}: Su servicio se completó antes de lo esperado. ¿Desea actualizar su próxima cita?`);
    alert(`Se ha enviado una notificación a ${reserva.cliente} sobre la posibilidad de actualizar su próxima cita.`);
}

// Función para confirmar una reserva
function confirmarReserva(reservaId) {
    const reserva = reservas.find(r => r.id === reservaId);
    if (reserva) {
        reserva.estado = 'confirmada';
        cargarReservas();
    }
}

// Función para cancelar una reserva
function cancelarReserva(reservaId) {
    if (confirm('¿Estás seguro de que deseas cancelar esta reserva?')) {
        const reserva = reservas.find(r => r.id === reservaId);
        if (reserva) {
            reserva.estado = 'cancelada';
            cargarReservas();
        }
    }
}

// Función para aplicar filtros
function aplicarFiltros() {
    const fecha = document.getElementById('filterDate').value;
    const estado = document.getElementById('filterStatus').value;
    
    cargarReservas({ fecha, estado });
}

// Cargar reservas al iniciar
document.addEventListener('DOMContentLoaded', () => {
    cargarReservas();
}); 