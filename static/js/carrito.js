
document.addEventListener('DOMContentLoaded', function () {
    const radios = document.querySelectorAll('input[name="metodo_pago"]');
    const camposTarjeta = document.getElementById('campos-tarjeta');
    const mensajeOxxo = document.getElementById('mensaje-oxxo');
    const mensajePaypal = document.getElementById('mensaje-paypal');
    const form = document.getElementById('form-pago');
    const envioEstandarRadio = document.getElementById('envio-estandar');
    const formEnvioEstandar = document.getElementById('form-envio-estandar');

    const estadoSelect = document.getElementById('estado');
    const envioSpan = document.getElementById('envio');
    const subtotalSpan = document.getElementById('subtotal');
    const impuestoSpan = document.getElementById('impuesto');
    const totalSpan = document.getElementById('total');

    const costosEnvio = {
        "Jalisco": 150,
        "CDMX": 180,
        "Nuevo León": 200,
        // Otros estados...
    };

    estadoSelect.addEventListener('change', function () {
        actualizarTotales();
    });

    envioEstandarRadio.addEventListener('change', function () {
        if (envioEstandarRadio.checked) {
            formEnvioEstandar.style.display = 'block';
        }
    });

    document.querySelectorAll('input[name="metodo_envio"]').forEach(radio => {
        if (radio.id !== 'envio-estandar') {
            radio.addEventListener('change', () => {
                formEnvioEstandar.style.display = 'none';
            });
        }
    });

    function ocultarTodo() {
        camposTarjeta.style.display = 'none';
        mensajeOxxo.style.display = 'none';
        mensajePaypal.style.display = 'none';

        camposTarjeta.querySelectorAll('input').forEach(input => {
            input.required = false;
            input.value = '';
        });
    }

    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            ocultarTodo();

            if (radio.value === 'Tarjeta') {
                camposTarjeta.style.display = 'block';
                camposTarjeta.querySelectorAll('input').forEach(input => input.required = true);
            } else if (radio.value === 'OXXO') {
                mensajeOxxo.style.display = 'block';
            } else if (radio.value === 'PayPal') {
                mensajePaypal.style.display = 'block';
            }
        });
    });

    form.addEventListener('submit', function (event) {
        const metodoPago = document.querySelector('input[name="metodo_pago"]:checked');
        if (!metodoPago) {
            event.preventDefault();
            alert("Por favor selecciona un método de pago.");
            return;
        }

        if (metodoPago.value === 'Tarjeta') {
            const numTarjeta = form.querySelector('input[name="num_tarjeta"]').value.trim();
            const vencimiento = form.querySelector('input[name="vencimiento"]').value.trim();
            const cvv = form.querySelector('input[name="cvv"]').value.trim();

            const tarjetaRegex = /^\d{16}$/;
            const vencimientoRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;
            const cvvRegex = /^\d{3,4}$/;

            if (!tarjetaRegex.test(numTarjeta)) {
                event.preventDefault();
                alert("El número de tarjeta debe tener 16 dígitos.");
                return;
            }
            if (!vencimientoRegex.test(vencimiento)) {
                event.preventDefault();
                alert("La fecha debe estar en formato MM/AA.");
                return;
            }
            if (!cvvRegex.test(cvv)) {
                event.preventDefault();
                alert("El CVV debe tener 3 o 4 dígitos.");
                return;
            }
        }
    });
    document.querySelectorAll('.eliminar').forEach(button => {
        button.addEventListener('click', function () {
            let fila = this.closest('tr');
            let id = fila.dataset.id;
            fetch(`/eliminar_carrito/${id}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fila.remove();
                    if (document.querySelectorAll('#tabla-carrito tbody tr').length === 0) {
                        document.getElementById('carrito-container').innerHTML = '<p id="mensaje-vacio">🛒 El carrito está vacío.</p>';
                    }
                    actualizarTotales();
                } else {
                    alert('Error al eliminar el artículo');
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // ✅ Evento para cambiar cantidad
    document.querySelectorAll('.cantidad').forEach(input => {
        input.addEventListener('change', function () {
            const fila = this.closest('tr');
            const productoId = fila.getAttribute('data-id');
            const nuevaCantidad = parseInt(this.value);

            console.log("🔄 Cambiando cantidad:", { productoId, nuevaCantidad });

            fetch('/actualizar_carrito', {  // Asegúrate que no tenga `/undefined`
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: productoId, cantidad: nuevaCantidad })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    const precio = parseFloat(this.getAttribute('data-precio'));
                    const nuevoTotal = (precio * nuevaCantidad).toFixed(2);
                    fila.querySelector('.total').textContent = `$${nuevoTotal}`;
                } else {
                    alert('❌ Error al actualizar la cantidad en el carrito.');
                }
            });
        });
    });

    // ✅ Calcula totales generales
    function actualizarTotales() {
        let subtotal = 0;

        document.querySelectorAll(".cantidad").forEach(input => {
            let cantidad = parseInt(input.value);
            let precio = parseFloat(input.dataset.precio);
            subtotal += cantidad * precio;
        });

        let impuesto = subtotal * 0.16;
        let estado = estadoSelect?.value;
        let costoEnvio = (estado === 'Sinaloa') ? 0 : (costosEnvio[estado] || 0);

        subtotalSpan.textContent = subtotal.toFixed(2);
        impuestoSpan.textContent = impuesto.toFixed(2);
        envioSpan.textContent = costoEnvio.toFixed(2);
        totalSpan.textContent = (subtotal + impuesto + costoEnvio).toFixed(2);
    }

    actualizarTotales();

    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', function () {
            this.style.transition = 'transform 0.2s ease';
            this.style.transform = 'scale(1.05)';
        });

        input.addEventListener('blur', function () {
            this.style.transition = 'transform 0.2s ease';
            this.style.transform = 'scale(1)';
        });
    });

    document.getElementById('btnProcesar').addEventListener('click', function () {
        const form = document.getElementById('form-pago');
        const formData = new FormData(form);

        const modalCargando = new bootstrap.Modal(document.getElementById('modalCargando'));
        modalCargando.show();

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            modalCargando.hide();
            const modalResultado = new bootstrap.Modal(document.getElementById('modalResultado'));
            const contenido = document.getElementById('resultadoContenido');

            if (data.success) {
                contenido.innerHTML = `
                    <div class="text-success display-4">✔️</div>
                    <h4 class="mt-2">¡Pago realizado con éxito!</h4>
                    <p>${data.message}</p>
                    <a href="/cliente" class="btn btn-success mt-3">Aceptar</a>
                `;
            } else {
                contenido.innerHTML = `
                    <div class="text-danger display-4">❌</div>
                    <h4 class="mt-2">Pago no realizado</h4>
                    <p>${data.message}</p>
                    <button class="btn btn-secondary mt-3" data-bs-dismiss="modal">Intentar de nuevo</button>
                `;
            }

            modalResultado.show();
        })
        .catch(err => {
            modalCargando.hide();
            const modalResultado = new bootstrap.Modal(document.getElementById('modalResultado'));
            const contenido = document.getElementById('resultadoContenido');
            contenido.innerHTML = `
                <div class="text-danger display-4">⚠️</div>
                <h4 class="mt-2">Error inesperado</h4>
                <p>Ocurrió un problema al procesar tu pago. Intenta más tarde.</p>
                <button class="btn btn-secondary mt-3" data-bs-dismiss="modal">Cerrar</button>
            `;
            modalResultado.show();
        });
    });
});

