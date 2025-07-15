document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (password !== confirmPassword) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Las contraseñas no coinciden',
            confirmButtonColor: '#d4af37'
        });
        return;
    }
    
    const userData = {
        nombre: document.getElementById('nombre').value,
        telefono: document.getElementById('telefono').value,
        email: document.getElementById('email').value,
        password: password
    };
    
    try {
        const response = await fetch('http://localhost:5000/api/auth/registro/cliente', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok) {
            // Guardar el token en localStorage
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('userData', JSON.stringify(data.cliente));
            
            Swal.fire({
                icon: 'success',
                title: '¡Registro exitoso!',
                text: 'Ahora puedes iniciar sesión.',
                confirmButtonColor: '#d4af37'
            }).then(() => {
                window.location.href = 'login.html';
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error || 'Error en el registro',
                confirmButtonColor: '#d4af37'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al conectar con el servidor',
            confirmButtonColor: '#d4af37'
        });
    }
});