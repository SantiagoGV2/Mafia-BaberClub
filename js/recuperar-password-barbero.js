// Lógica para recuperar contraseña de barberos

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('recoverForm');
    if (!form) return;
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        fetch('http://localhost:5000/api/barberos/recuperar-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                window.location.href = 'verificar-codigo.html?email=' + encodeURIComponent(email) + '&tipo=barbero';
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
}); 