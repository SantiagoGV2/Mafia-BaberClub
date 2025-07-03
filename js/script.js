// Función para verificar el estado de la autenticación
async function verificarAutenticacion() {
    const token = localStorage.getItem('token');
    const userSection = document.getElementById('userSection');
    const loginSection = document.getElementById('loginSection');

    if (!token) {
        if (userSection) userSection.classList.add('d-none');
        if (loginSection) loginSection.classList.remove('d-none');
        return null;
    }

    try {
        const response = await fetch('http://localhost:5000/api/auth/perfil', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Token inválido');
        }

        const data = await response.json();
        
        if (userSection && loginSection) {
            userSection.classList.remove('d-none');
            loginSection.classList.add('d-none');

            // Mostrar iniciales y nombre
            const initials = data.cli_nombre ? data.cli_nombre.split(' ').map(n => n[0]).join('').toUpperCase() 
                          : data.bar_nombre.split(' ').map(n => n[0]).join('').toUpperCase();
            document.getElementById('userInitials').textContent = initials;
            document.getElementById('userName').textContent = data.cli_nombre || data.bar_nombre;

            // Configurar botón de logout
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', function() {
                    localStorage.removeItem('token');
                    window.location.href = 'login.html';
                });
            }
        }

        return data;
    } catch (error) {
        console.error('Error al verificar token:', error);
        localStorage.removeItem('token');
        if (userSection) userSection.classList.add('d-none');
        if (loginSection) loginSection.classList.remove('d-none');
        return null;
    }
}

// Función para manejar el inicio de sesión
async function iniciarSesion(email, password, role = 'cliente') {
    try {
        const endpoint = role === 'barbero' ? '/login/barbero' : '/login/cliente';
        const response = await fetch(`http://localhost:5000/api/auth${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al iniciar sesión');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        return role === 'barbero' ? data.barbero : data.cliente;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Función para manejar el registro
async function registrarUsuario(nombre, email, password, telefono) {
    try {
        const response = await fetch('http://localhost:5000/api/auth/registro/cliente', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre, email, password, telefono })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al registrar usuario');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        return data.cliente;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Verificar autenticación al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    verificarAutenticacion();
}); 