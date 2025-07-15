// Lógica para actualizar la contraseña de barberos

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('passwordForm');
    if (!form) return;
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const params = new URLSearchParams(window.location.search);
        const email = params.get('email');
        const codigo = params.get('codigo');
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
        fetch('http://localhost:5000/api/barberos/nueva-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, codigo, nuevaPassword: password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Contraseña actualizada!',
                    text: 'Ahora puedes iniciar sesión con tu nueva contraseña.',
                    confirmButtonColor: '#d4af37'
                }).then(() => {
                    window.location.href = 'login.html';
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Error',
                    confirmButtonColor: '#d4af37'
                });
            }
        });
    });

    // Validación visual de requisitos de contraseña
    const password = document.getElementById('password');
    const requirements = {
        length: document.getElementById('length'),
        uppercase: document.getElementById('uppercase'),
        lowercase: document.getElementById('lowercase'),
        number: document.getElementById('number'),
        special: document.getElementById('special')
    };
    if (password) {
        password.addEventListener('input', function() {
            const value = this.value;
            // Longitud
            if (value.length >= 8) {
                requirements.length.classList.add('valid');
                requirements.length.classList.remove('invalid');
                requirements.length.querySelector('i').classList.replace('bi-x-circle', 'bi-check-circle');
            } else {
                requirements.length.classList.remove('valid');
                requirements.length.classList.add('invalid');
                requirements.length.querySelector('i').classList.replace('bi-check-circle', 'bi-x-circle');
            }
            // Mayúscula
            if (/[A-Z]/.test(value)) {
                requirements.uppercase.classList.add('valid');
                requirements.uppercase.classList.remove('invalid');
                requirements.uppercase.querySelector('i').classList.replace('bi-x-circle', 'bi-check-circle');
            } else {
                requirements.uppercase.classList.remove('valid');
                requirements.uppercase.classList.add('invalid');
                requirements.uppercase.querySelector('i').classList.replace('bi-check-circle', 'bi-x-circle');
            }
            // Minúscula
            if (/[a-z]/.test(value)) {
                requirements.lowercase.classList.add('valid');
                requirements.lowercase.classList.remove('invalid');
                requirements.lowercase.querySelector('i').classList.replace('bi-x-circle', 'bi-check-circle');
            } else {
                requirements.lowercase.classList.remove('valid');
                requirements.lowercase.classList.add('invalid');
                requirements.lowercase.querySelector('i').classList.replace('bi-check-circle', 'bi-x-circle');
            }
            // Número
            if (/[0-9]/.test(value)) {
                requirements.number.classList.add('valid');
                requirements.number.classList.remove('invalid');
                requirements.number.querySelector('i').classList.replace('bi-x-circle', 'bi-check-circle');
            } else {
                requirements.number.classList.remove('valid');
                requirements.number.classList.add('invalid');
                requirements.number.querySelector('i').classList.replace('bi-check-circle', 'bi-x-circle');
            }
            // Especial
            if (/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
                requirements.special.classList.add('valid');
                requirements.special.classList.remove('invalid');
                requirements.special.querySelector('i').classList.replace('bi-x-circle', 'bi-check-circle');
            } else {
                requirements.special.classList.remove('valid');
                requirements.special.classList.add('invalid');
                requirements.special.querySelector('i').classList.replace('bi-check-circle', 'bi-x-circle');
            }
        });
    }

    // Mostrar/ocultar contraseña
    function togglePasswordVisibility(inputId, buttonId) {
        const input = document.getElementById(inputId);
        const button = document.getElementById(buttonId);
        if (!input || !button) return;
        button.addEventListener('click', function() {
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-eye');
                icon.classList.toggle('bi-eye-slash');
            }
        });
    }
    togglePasswordVisibility('password', 'togglePassword');
    togglePasswordVisibility('confirmPassword', 'toggleConfirmPassword');
}); 