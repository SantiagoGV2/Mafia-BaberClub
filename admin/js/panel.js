// En js/panel-barbero.js
document.addEventListener('DOMContentLoaded', () => {
    // --- 1. VERIFICACIÓN DE SEGURIDAD ---
    const token = localStorage.getItem('token');
    const userData = JSON.parse(localStorage.getItem('userData'));

    if (!token || !userData || userData.tipo !== 'barbero') {
        localStorage.clear();
        window.location.href = '../login.html';
        return;
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            // 1. Prevenimos que el enlace navegue a una página nueva
            e.preventDefault();

            // 2. Limpiamos completamente los datos de sesión del navegador
            localStorage.clear();

            // 3. Redirigimos al usuario a la página de login
            window.location.href = '../login.html'; 
        });
    }

    // --- 2. ELEMENTOS DEL DOM Y VARIABLES GLOBALES ---
    const barberoNombreEl = document.getElementById('barberoNombre');
    const reservasContainer = document.getElementById('reservasContainer');
    const reservaCardTemplate = document.getElementById('reserva-card-template');
    
    let todasLasReservas = [];
    const activeTimers = {};

    // --- 3. LÓGICA PRINCIPAL ---

    const initPanel = async () => {
        barberoNombreEl.textContent = `Bienvenido, ${userData.nombre}`;
        setupEventListeners(); // Configuramos los listeners UNA SOLA VEZ
        await cargarReservas();
    };

    const cargarReservas = async () => {
        reservasContainer.innerHTML = `<div class="col-12 text-center"><div class="spinner-border text-gold"></div></div>`;
        try {
            const response = await fetch('http://localhost:5000/api/reservas/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('No se pudieron cargar las reservas.');
            
            todasLasReservas = await response.json();
            renderReservas(); 
        } catch (error) {
            reservasContainer.innerHTML = `<div class="col"><p class="text-danger">${error.message}</p></div>`;
            console.error(error);
        }
    };

    const renderReservas = () => {
        const estadoFiltro = document.querySelector('.filtro-btn.active')?.dataset.estado || 'todos';
        reservasContainer.innerHTML = '';

        const reservasFiltradas = estadoFiltro === 'todos'
            ? todasLasReservas
            : todasLasReservas.filter(r => r.res_estado === estadoFiltro);

        if (reservasFiltradas.length === 0) {
            reservasContainer.innerHTML = '<div class="col-12 text-center"><p class="text-muted mt-4">No hay reservas que coincidan con los filtros.</p></div>';
            return;
        }

        reservasFiltradas.forEach(reserva => {
            const cardClone = reservaCardTemplate.content.cloneNode(true);
            const cardContainer = cardClone.querySelector('.col-md-6');
            cardContainer.dataset.id = reserva.res_id;
            
            const cardElement = cardContainer.querySelector('.reservation-card');
            cardElement.dataset.startTime = activeTimers[`timer-${reserva.res_id}`]?.startTime || '';

            cardContainer.innerHTML = crearTarjetaHTML(reserva);
            reservasContainer.appendChild(cardContainer);

            if (reserva.res_estado === 'en-progreso') {
                iniciarCronometro(reserva.res_id);
            }
        });
    };
    
    const crearTarjetaHTML = (reserva) => {
        let botonesHTML = '';
        switch (reserva.res_estado) {
            case 'pendiente':
                botonesHTML = `<button class="btn btn-success btn-sm" data-action="confirmar">Confirmar</button>
                               <button class="btn btn-danger btn-sm" data-action="cancelar">Rechazar</button>`;
                break;
            case 'confirmada':
                botonesHTML = `<button class="btn btn-primary w-100" data-action="iniciar">Iniciar Servicio</button>`;
                break;
            case 'en-progreso':
                botonesHTML = `<button class="btn btn-info w-100" data-action="terminar">Terminar Servicio</button>`;
                break;
            default:
                botonesHTML = `<p class="text-muted text-center small mb-0 text-capitalize">Reserva ${reserva.res_estado}</p>`;
                break;
        }

        return `
        <div class="card h-100 shadow-sm reservation-card" data-start-time="">
            <div class="card-header d-flex justify-content-between align-items-center fw-bold">
                <span class="reserva-hora">${reserva.res_hora_inicio}</span>
                <span class="reserva-estado-badge status-badge status-${reserva.res_estado}">${reserva.res_estado}</span>
            </div>
            <div class="card-body">
                <h5 class="card-title">${reserva.ser_nombre}</h5>
                <p class="mb-1"><i class="bi bi-person me-2 text-gold"></i>${reserva.cli_nombre}</p>
                <p class="mb-2"><i class="bi bi-phone me-2 text-gold"></i><a href="tel:${reserva.cli_telefono}" class="text-decoration-none text-dark">${reserva.cli_telefono}</a></p>
                
                <p class="mb-2 fw-bold"><i class="bi bi-cash-coin me-2 text-success"></i>$${parseFloat(reserva.res_total_pagar).toLocaleString('es-CO')}</p>

                ${reserva.res_notas ? `
                <div class="reserva-notas bg-light p-2 rounded">
                    <small class="text-muted d-block"><i class="bi bi-chat-left-text me-1"></i>Notas del cliente:</small>
                    <small>${reserva.res_notas}</small>
                </div>
                ` : ''}
            </div>
            <div class="card-footer bg-light">
                <div class="cronometro-container text-center my-2 ${reserva.res_estado === 'en-progreso' ? '' : 'd-none'}">
                    <h4 class="display-6"><i class="bi bi-stopwatch text-danger me-2"></i><span class="cronometro-tiempo">00:00</span></h4>
                </div>
                <div class="acciones-container d-flex gap-2 justify-content-end">${botonesHTML}</div>
            </div>
        </div>`;
    };

    const setupEventListeners = () => {
        // Un solo listener para todas las acciones de las tarjetas
        reservasContainer.addEventListener('click', (e) => {
            const button = e.target.closest('button[data-action]');
            if (!button) return;

            const cardContainer = e.target.closest('.col-md-6');
            const reservaId = cardContainer.dataset.id;
            const action = button.dataset.action;

            switch (action) {
                case 'confirmar': actualizarEstado(reservaId, 'confirmada'); break;
                case 'cancelar': if (confirm('¿Seguro?')) { actualizarEstado(reservaId, 'cancelada'); } break;
                case 'iniciar': actualizarEstado(reservaId, 'en-progreso'); break;
                case 'terminar': terminarServicio(reservaId); break;
            }
        });

        // Listeners para los botones de filtro
        document.querySelector('.filtros-reservas').addEventListener('click', (e) => {
            const button = e.target.closest('.filtro-btn');
            if (!button) return;

            document.querySelectorAll('.filtro-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            renderReservas();
        });
    };

    const actualizarEstado = async (id, nuevoEstado) => {
        try {
            await fetch(`http://localhost:5000/api/reservas/${id}/estado`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ estado: nuevoEstado })
            });
            // Actualizamos el estado en el array local y volvemos a renderizar
            const reserva = todasLasReservas.find(r => r.res_id == id);
            if (reserva) reserva.res_estado = nuevoEstado;
            renderReservas();
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudo actualizar el estado.',
                confirmButtonColor: '#d4af37'
            });
        }
    };
    
    const iniciarCronometro = (reservaId) => {
        const timerId = `timer-${reservaId}`;
        if (activeTimers[timerId]) return;

        const cardContainer = document.querySelector(`.col-md-6[data-id='${reservaId}']`);
        if (!cardContainer) return;
        
        const cardElement = cardContainer.querySelector('.reservation-card');
        const cronometroDisplay = cardElement.querySelector('.cronometro-tiempo');
        
        const startTime = Date.now();
        cardElement.dataset.startTime = startTime;

        activeTimers[timerId] = {
            interval: setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
                const seconds = String(elapsed % 60).padStart(2, '0');
                if (cronometroDisplay) cronometroDisplay.textContent = `${minutes}:${seconds}`;
            }, 1000),
            startTime: startTime
        };
    };

    const terminarServicio = async (reservaId) => {
        const timerId = `timer-${reservaId}`;
        const timerData = activeTimers[timerId];

        if (!timerData) {
            console.error("No se encontró un cronómetro activo para esta reserva.");
            await actualizarEstado(reservaId, 'completada'); // Completar aunque no haya timer
            return;
        }

        clearInterval(timerData.interval);
        delete activeTimers[timerId];

        const duracionRealMinutos = Math.round((Date.now() - timerData.startTime) / 60000);
        const duracionFinal = duracionRealMinutos > 0 ? duracionRealMinutos : 1;

        try {
            await fetch(`http://localhost:5000/api/reservas/${reservaId}/tiempo`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ tiempo_real_duracion: duracionFinal })
            });
            await actualizarEstado(reservaId, 'completada');
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al finalizar el servicio.',
                confirmButtonColor: '#d4af37'
            });
        }
    };

    // --- 4. INICIO DE LA APLICACIÓN ---
    initPanel();
});