// Lógica para verificar código de recuperación de barberos

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('verifyForm');
    if (!form) return;
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const params = new URLSearchParams(window.location.search);
        const email = params.get('email');
        const code = Array.from(document.querySelectorAll('.code-input')).map(input => input.value).join('');
        fetch('http://localhost:5000/api/barberos/verificar-codigo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, codigo: code })
        })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                window.location.href = 'nueva-password.html?email=' + encodeURIComponent(email) + '&codigo=' + code + '&tipo=barbero';
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

    // Lógica de inputs de código (salto, retroceso, pegado)
    const codeInputs = document.querySelectorAll('.code-input');
    codeInputs.forEach((input, idx) => {
        input.addEventListener('input', function(e) {
            if (this.value.length === 1 && idx < codeInputs.length - 1) {
                codeInputs[idx + 1].focus();
            }
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && idx > 0) {
                codeInputs[idx - 1].focus();
            }
        });
        input.addEventListener('paste', function(e) {
            const paste = (e.clipboardData || window.clipboardData).getData('text');
            if (/^[0-9]{6}$/.test(paste)) {
                e.preventDefault();
                paste.split('').forEach((num, i) => {
                    if (codeInputs[i]) codeInputs[i].value = num;
                });
                codeInputs[5].focus();
            }
        });
    });

    // Timer de 5 minutos
    const countdownEl = document.getElementById('countdown');
    const resendLink = document.getElementById('resendCode');
    if (countdownEl) {
        let timer = 300; // 5 minutos en segundos
        resendLink.style.display = 'none';
        const interval = setInterval(() => {
            const minutes = String(Math.floor(timer / 60)).padStart(2, '0');
            const seconds = String(timer % 60).padStart(2, '0');
            countdownEl.textContent = `${minutes}:${seconds}`;
            if (--timer < 0) {
                clearInterval(interval);
                countdownEl.textContent = '00:00';
                resendLink.style.display = 'inline';
            }
        }, 1000);
    }
}); 