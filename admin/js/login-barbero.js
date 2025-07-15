document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');


    // Manejar inicio de sesión
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('http://localhost:5000/api/auth/login/barbero', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('userData', JSON.stringify(data.barbero));
                window.location.href = './pages/panel-barbero.html';
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Credenciales incorrectas',
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
});