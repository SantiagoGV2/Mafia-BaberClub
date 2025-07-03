document.addEventListener('DOMContentLoaded', async () => {
    const serviceContainer = document.getElementById('service-list-container');
    if (!serviceContainer) return;

    serviceContainer.innerHTML = '<div class="text-center"><div class="spinner-border text-gold" role="status"><span class="visually-hidden">Cargando...</span></div></div>';

    try {
        // Usamos el endpoint de tu servicios.py
        const response = await fetch('http://localhost:5000/api/servicios/');
        if (!response.ok) {
            throw new Error('No se pudieron cargar los servicios.');
        }
        const services = await response.json();

        serviceContainer.innerHTML = ''; // Limpiamos el spinner

        services.forEach(service => {
            const serviceCard = document.createElement('div');
            serviceCard.className = 'col-md-4 animate__animated animate__fadeInUp';
            
            // Creamos el HTML para cada tarjeta de servicio
            serviceCard.innerHTML = `
                <div class="card service-card h-100">
                    <div class="card-body p-4 text-center">
                        <div class="service-icon">
                            <i class="bi bi-scissors"></i> </div>
                        <h3 class="h4">${service.ser_nombre}</h3>
                        <span class="service-time">≈ ${service.ser_duracion} min</span>
                        <p class="text-muted">${service.ser_descripcion}</p>
                        <p class="service-price text-gold">$${parseFloat(service.ser_precio).toLocaleString('es-CO')}</p>
                        <a href="reservar.html?service=${service.ser_id}" class="btn btn-gold btn-sm mt-3">Reservar</a>
                    </div>
                </div>
            `;
            serviceContainer.appendChild(serviceCard);
        });

    } catch (error) {
        console.error('Error:', error);
        serviceContainer.innerHTML = '<p class="text-center text-danger">Error al cargar los servicios. Intenta de nuevo más tarde.</p>';
    }
});