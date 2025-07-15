document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        // Si no hay token, redirigir al login
        window.location.href = `login.html?redirect=${encodeURIComponent(window.location.href)}`;
        return;
    }

    // Elementos del DOM
    const barberSelectionContainer = document.getElementById('barberSelection');
    const fechaInput = document.getElementById('fecha');
    const timeSlotsContainer = document.getElementById('timeSlots');
    const reservationForm = document.getElementById('reservationForm');
    const summaryBarber = document.getElementById('summaryBarber');
    const summaryDateTime = document.getElementById('summaryDateTime');
    const summaryService = document.getElementById('summaryService');
    const summaryTotal = document.getElementById('summaryTotal');
    const notasInput = document.getElementById('notas');

    let serviciosDisponibles = [];
    let barberosDisponibles = [];
    let reservaActual = {
        barbero_id: null,
        servicio_id: null,
        fecha: null,
        hora_inicio: null
    };

    // --- 1. Cargar datos iniciales (Barberos y Servicios) ---
    async function cargarDatosIniciales() {
        try {
            // Cargar barberos
            const barberosResponse = await fetch('http://localhost:5000/api/barberos/barberos', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            barberosDisponibles = await barberosResponse.json();
            renderBarberos();

            // *** CORRECCIÓN IMPORTANTE ***
            // Usamos el endpoint correcto para obtener todos los servicios.
            const serviciosResponse = await fetch(`http://localhost:5000/api/servicios/`);
            if (!serviciosResponse.ok) throw new Error('Error al cargar servicios');
            serviciosDisponibles = await serviciosResponse.json();
            
            // Si viene un servicio en la URL, seleccionarlo
            const urlParams = new URLSearchParams(window.location.search);
            const serviceIdFromUrl = urlParams.get('service');
            if (serviceIdFromUrl) {
                // Convertimos el ID de la URL a número para buscarlo
                seleccionarServicio(parseInt(serviceIdFromUrl, 10));
            } else if (serviciosDisponibles.length > 0) {
                // O seleccionar el primero por defecto si no viene ninguno
                seleccionarServicio(serviciosDisponibles[0].ser_id);
            }

        } catch (error) {
            console.error("Error al cargar datos iniciales:", error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los datos necesarios para la reserva.',
                confirmButtonColor: '#d4af37'
            });
        }
    }

    // --- 2. Renderizar y manejar selecciones ---
    function renderBarberos() {
        barberSelectionContainer.innerHTML = '';
        barberosDisponibles.forEach(barbero => {
            const card = document.createElement('div');
            card.className = 'col-md-4 barber-card';
            card.dataset.barberId = barbero.bar_id;
            card.innerHTML = `
                <div class="card border-0 h-100 text-center p-3">
                    <img src="${barbero.bar_imagen || '/assets/img/default-avatar.png'}" alt="${barbero.bar_nombre}" class="barber-img mx-auto mb-2">
                    <h5 class="h6 mb-1">${barbero.bar_nombre}</h5>
                    <small class="text-muted">${barbero.bar_especialidad}</small>
                </div>
            `;
            card.addEventListener('click', () => seleccionarBarbero(barbero.bar_id));
            barberSelectionContainer.appendChild(card);
        });
    }

    function seleccionarServicio(servicioId) {
        const servicio = serviciosDisponibles.find(s => s.ser_id === servicioId);
        if (!servicio) {
            console.error(`Servicio con ID ${servicioId} no encontrado.`);
            // Opcional: seleccionar el primer servicio como fallback
            if(serviciosDisponibles.length > 0) {
               return seleccionarServicio(serviciosDisponibles[0].ser_id);
            }
            return;
        }

        reservaActual.servicio_id = servicio.ser_id;
        document.getElementById('serviceTitle').textContent = servicio.ser_nombre;
        document.getElementById('serviceTime').textContent = `≈ ${servicio.ser_duracion} min`;
        document.getElementById('servicePrice').textContent = `$${parseFloat(servicio.ser_precio).toLocaleString('es-CO')}`;
        
        actualizarResumen();
        actualizarHorariosDisponibles();
    }
    
    function seleccionarBarbero(barberoId) {
        reservaActual.barbero_id = barberoId;
        document.querySelectorAll('.barber-card').forEach(c => c.classList.remove('selected'));
        document.querySelector(`.barber-card[data-barber-id='${barberoId}']`).classList.add('selected');
        
        actualizarResumen();
        actualizarHorariosDisponibles();
    }

    function seleccionarHora(hora) {
        reservaActual.hora_inicio = hora;
        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
        const slot = Array.from(document.querySelectorAll('.time-slot')).find(s => s.textContent === hora);
        if (slot) slot.classList.add('selected');

        actualizarResumen();
    }


    // --- 3. Lógica de Disponibilidad ---
    async function actualizarHorariosDisponibles() {
        if (!reservaActual.barbero_id || !reservaActual.fecha) {
            timeSlotsContainer.innerHTML = '<span class="text-muted">Selecciona un barbero y una fecha.</span>';
            return;
        }
    
        timeSlotsContainer.innerHTML = '<div class="spinner-border spinner-border-sm text-gold" role="status"><span class="visually-hidden">Cargando...</span></div>';
    
        try {
            const response = await fetch(`http://localhost:5000/api/reservas/disponibilidad?barbero_id=${reservaActual.barbero_id}&fecha=${reservaActual.fecha}`);
            if (!response.ok) {
                throw new Error(`Error ${response.status} del servidor.`);
            }
            const data = await response.json();
    
            // --- MÉTODO CORREGIDO Y MÁS ROBUSTO ---
            // Mapeo de número de día (0=Domingo) a los strings de tu BD
            const diasSemana = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'];
            // new Date() necesita un ajuste de zona horaria para que getDay() sea correcto
            const fechaSeleccionada = new Date(reservaActual.fecha + 'T12:00:00'); 
            const diaDeLaSemana = diasSemana[fechaSeleccionada.getDay()];
            
            // --- CONSEJO DE DEPURACIÓN ---
            // Abre la consola del navegador (F12) para ver estos mensajes. Te ayudarán a depurar.
            console.log("Día de la semana calculado:", diaDeLaSemana);
            console.log("Horarios recibidos de la API:", data.horario);
            // ------------------------------------
    
            const horarioBarbero = data.horario.find(h => h.hor_dia_semana === diaDeLaSemana);
    
            timeSlotsContainer.innerHTML = '';
            if (!horarioBarbero) {
                timeSlotsContainer.innerHTML = '<span class="text-muted">El barbero no trabaja este día.</span>';
                return;
            }
    
            // Lógica mejorada para generar los slots de tiempo
            const servicioSeleccionado = serviciosDisponibles.find(s => s.ser_id === reservaActual.servicio_id);
            const duracionServicio = servicioSeleccionado ? parseInt(servicioSeleccionado.ser_duracion, 10) : 30; // Intervalo de 30 min por defecto
    
            let horaActual = new Date(`${reservaActual.fecha}T${horarioBarbero.hor_hora_inicio}`);
            const horaFin = new Date(`${reservaActual.fecha}T${horarioBarbero.hor_hora_fin}`);
    
            while (horaActual < horaFin) {
                const horaString24 = horaActual.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }); // Formato HH:mm
                const horaStringAmPm = horaActual.toLocaleTimeString('es-ES', { hour: 'numeric', minute: '2-digit', hour12: true });
    
                const timeSlot = document.createElement('span');
                timeSlot.className = 'time-slot';
                timeSlot.textContent = horaStringAmPm;
                timeSlot.dataset.hora24 = horaString24;
    
                // Verificar si el slot está ocupado
                const finSlot = new Date(horaActual.getTime() + duracionServicio * 60000);
                const estaOcupado = data.reservas.some(reserva => {
                    const inicioReserva = new Date(`${reservaActual.fecha}T${reserva.res_hora_inicio}`);
                    const finReserva = new Date(`${reservaActual.fecha}T${reserva.res_hora_fin}`);
                    // Comprueba si hay solapamiento
                    return (horaActual < finReserva && finSlot > inicioReserva);
                });
    
                if (estaOcupado || finSlot > horaFin) {
                    timeSlot.classList.add('booked'); // Marcar como ocupado si se solapa o si no hay tiempo suficiente
                } else {
                    timeSlot.addEventListener('click', () => seleccionarHora(horaStringAmPm));
                }
    
                timeSlotsContainer.appendChild(timeSlot);
                
                // Incrementar la hora por la duración del servicio para el siguiente slot
                horaActual.setMinutes(horaActual.getMinutes() + duracionServicio);
            }
            
            if (timeSlotsContainer.innerHTML === '') {
                 timeSlotsContainer.innerHTML = '<span class="text-muted">No hay horarios disponibles para este día.</span>';
            }
    
        } catch (error) {
            console.error("Error al obtener horarios:", error);
            timeSlotsContainer.innerHTML = '<span class="text-danger">Error al cargar horarios. Inténtalo de nuevo.</span>';
        }
    }

    // --- 4. Actualizar el Resumen ---
    function actualizarResumen() {
        const barbero = barberosDisponibles.find(b => b.bar_id === reservaActual.barbero_id);
        const servicio = serviciosDisponibles.find(s => s.ser_id === reservaActual.servicio_id);
        
        summaryBarber.textContent = barbero ? barbero.bar_nombre : '---';
        summaryService.textContent = servicio ? servicio.ser_nombre : '---';
        summaryTotal.textContent = servicio ? `$${parseFloat(servicio.ser_precio).toLocaleString('es-CO')}` : '$0';
        
        if (reservaActual.fecha && reservaActual.hora_inicio) {
            const fecha = new Date(reservaActual.fecha + 'T00:00:00');
            const options = { weekday: 'long', day: 'numeric', month: 'short' };
            const fechaFormateada = fecha.toLocaleDateString('es-ES', options);
            summaryDateTime.textContent = `${fechaFormateada} - ${reservaActual.hora_inicio}`;
        } else {
            summaryDateTime.textContent = '---';
        }
    }


    // --- 5. Enviar el Formulario ---
    reservationForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!reservaActual.servicio_id || !reservaActual.barbero_id || !reservaActual.fecha || !reservaActual.hora_inicio) {
            Swal.fire({
                icon: 'warning',
                title: 'Campos incompletos',
                text: 'Por favor, completa todos los campos para continuar.',
                confirmButtonColor: '#d4af37'
            });
            return;
        }

        // Convertir hora de "2:00 p. m." a formato "14:00"
        const slotSeleccionado = document.querySelector('.time-slot.selected');
        const hora24 = slotSeleccionado.dataset.hora24;

        const datosReserva = {
            servicio_id: reservaActual.servicio_id,
            barbero_id: reservaActual.barbero_id,
            fecha: reservaActual.fecha,
            hora_inicio: hora24,
            notas: notasInput.value
        };

        try {
            const response = await fetch('http://localhost:5000/api/reservas/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(datosReserva)
            });

            const resultado = await response.json();

            if (!response.ok) {
                throw new Error(resultado.error || 'No se pudo crear la reserva.');
            }
            
            Swal.fire({
                icon: 'success',
                title: '¡Reserva creada!',
                text: 'Tu reserva fue creada exitosamente.',
                confirmButtonColor: '#d4af37'
            }).then(() => {
                window.location.href = 'mis-reservas.html';
            });

        } catch (error) {
            console.error('Error al enviar reserva:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message,
                confirmButtonColor: '#d4af37'
            });
        }
    });


    // --- Inicialización ---
    fechaInput.min = new Date().toISOString().split('T')[0];
    fechaInput.addEventListener('change', (e) => {
        reservaActual.fecha = e.target.value;
        actualizarHorariosDisponibles();
    });
    
    cargarDatosIniciales();
});