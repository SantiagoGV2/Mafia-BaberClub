document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    const reservationsContainer = document.getElementById('reservations-container');
    const detailsModal = new bootstrap.Modal(document.getElementById('detailsModal'));
    const modalBody = document.getElementById('modal-body-content');

    const cargarReservas = async () => {
        try {
            // Usamos el endpoint de reservas del cliente
            const response = await fetch('http://localhost:5000/api/reservas/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) {
                throw new Error('No se pudieron cargar tus reservas.');
            }

            const reservas = await response.json();
            renderReservas(reservas);

        } catch (error) {
            console.error("Error:", error);
            reservationsContainer.innerHTML = `<div class="col-12 text-center text-danger"><h3>Error al cargar reservas</h3><p>${error.message}</p></div>`;
        }
    };

    const renderReservas = (reservas) => {
        reservationsContainer.innerHTML = '';
        if (reservas.length === 0) {
            reservationsContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-calendar-x" style="font-size: 4rem; color: #ccc;"></i>
                    <h4 class="mt-3">No tienes reservas</h4>
                    <p class="text-muted">¡Anímate a programar tu próxima cita!</p>
                </div>`;
            return;
        }

        reservas.forEach(reserva => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4';
            
            const fecha = new Date(reserva.res_fecha + 'T00:00:00');
            const fechaFormateada = fecha.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
            const diaSemana = fecha.toLocaleDateString('es-ES', { weekday: 'long' });

            const hora = reserva.res_hora_inicio.substring(0, 5); // Tomar solo HH:mm

            col.innerHTML = `
                <div class="reservation-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5 class="card-title mb-1">${reserva.ser_nombre}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">con ${reserva.bar_nombre}</h6>
                            </div>
                            <span class="status-badge status-${reserva.res_estado}">${reserva.res_estado}</span>
                        </div>
                        <hr>
                        <p class="card-text mb-1">
                            <i class="bi bi-calendar-event me-2 text-gold"></i>
                            <strong class="text-capitalize">${diaSemana}</strong>, ${fechaFormateada}
                        </p>
                        <p class="card-text">
                            <i class="bi bi-clock me-2 text-gold"></i>
                            ${hora}
                        </p>
                        <div class="d-flex justify-content-end gap-2 mt-3">
                            <button class="btn btn-outline-dark btn-sm view-details" data-reserva-id="${reserva.res_id}">
                                <i class="bi bi-eye"></i> Ver Detalles
                            </button>
                            ${reserva.res_estado === 'pendiente' || reserva.res_estado === 'confirmada' ? `
                            <button class="btn btn-outline-primary btn-sm edit-reservation" data-reserva-id="${reserva.res_id}">
                                <i class="bi bi-pencil"></i> Editar
                            </button>
                            <button class="btn btn-outline-danger btn-sm cancel-reservation" data-reserva-id="${reserva.res_id}">
                                <i class="bi bi-x-lg"></i> Cancelar
                            </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            reservationsContainer.appendChild(col);
        });

        // Añadir Event Listeners a los nuevos botones
        addEventListeners();
    };

    const addEventListeners = () => {
        // Botones para cancelar
        document.querySelectorAll('.cancel-reservation').forEach(button => {
            button.addEventListener('click', (e) => {
                const reservaId = e.currentTarget.dataset.reservaId;
                if (confirm('¿Estás seguro de que deseas cancelar esta reserva?')) {
                    cancelarReserva(reservaId);
                }
            });
        });

        // Botones para ver detalles
        document.querySelectorAll('.view-details').forEach(button => {
            button.addEventListener('click', (e) => {
                const reservaId = e.currentTarget.dataset.reservaId;
                mostrarDetalles(reservaId);
            });
        });
        
        // Botones para editar (funcionalidad futura)
         document.querySelectorAll('.edit-reservation').forEach(button => {
            button.addEventListener('click', (e) => {
                const reservaId = e.currentTarget.dataset.reservaId;
                alert('La función para editar estará disponible próximamente. Por ahora, puedes cancelar y crear una nueva reserva.');
                // window.location.href = `editar-reserva.html?id=${reservaId}`;
            });
        });
    };

    const cancelarReserva = async (id) => {
        try {
            const response = await fetch(`http://localhost:5000/api/reservas/${id}/cancelar`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);

            alert(result.message);
            cargarReservas(); // Recargar la lista
        } catch (error) {
            console.error("Error al cancelar:", error);
            alert(error.message);
        }
    };
    
    const mostrarDetalles = async (id) => {
        try {
            const response = await fetch(`http://localhost:5000/api/reservas/${id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if(!response.ok) throw new Error('No se pudo cargar el detalle.');

            const reserva = await response.json();
            
            modalBody.innerHTML = `
                <p><strong>Servicio:</strong> ${reserva.ser_nombre}</p>
                <p><strong>Barbero:</strong> ${reserva.bar_nombre}</p>
                <p><strong>Fecha:</strong> ${new Date(reserva.res_fecha + 'T00:00:00').toLocaleDateString('es-ES', { dateStyle: 'full' })}</p>
                <p><strong>Hora:</strong> ${reserva.res_hora_inicio.substring(0,5)}</p>
                <p><strong>Estado:</strong> <span class="badge status-${reserva.res_estado}">${reserva.res_estado}</span></p>
                <p><strong>Total:</strong> $${parseFloat(reserva.res_total_pagar).toLocaleString('es-CO')}</p>
                ${reserva.res_notas ? `<p><strong>Notas:</strong> ${reserva.res_notas}</p>` : ''}
            `;
            detailsModal.show();

        } catch(error) {
            console.error("Error al mostrar detalles:", error);
            alert(error.message);
        }
    };

    // Carga inicial
    cargarReservas();
});