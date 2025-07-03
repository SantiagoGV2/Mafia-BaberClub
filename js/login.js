document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');


    // Manejar inicio de sesión
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('http://localhost:5000/api/auth/login/cliente', {
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
                localStorage.setItem('userData', JSON.stringify(data.cliente));
                window.location.href = '../index.html';
            } else {
                alert(data.error || 'Credenciales incorrectas');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al conectar con el servidor');
        }
    });
});