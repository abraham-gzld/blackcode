
    document.addEventListener("DOMContentLoaded", function () {
        const usuario = "{{ session.get('email', 'Invitado') }}"; 
        document.getElementById("userName").innerText = usuario;
    });
