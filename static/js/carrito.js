document.addEventListener('DOMContentLoaded', function () {
    // Mostrar los campos según el método de pago
    const radios = document.querySelectorAll('input[name="metodo_pago"]');
    const camposTarjeta = document.getElementById('campos-tarjeta');
    const mensajeOxxo = document.getElementById('mensaje-oxxo');
    const mensajePaypal = document.getElementById('mensaje-paypal');
    const form = document.getElementById('form-pago');

    function ocultarTodo() {
        camposTarjeta.style.display = 'none';  // Ocultar campos de tarjeta
        mensajeOxxo.style.display = 'none';   // Ocultar mensaje de OXXO
        mensajePaypal.style.display = 'none'; // Ocultar mensaje de PayPal

        camposTarjeta.querySelectorAll('input').forEach(input => {
            input.required = false;
            input.value = ''; // Limpiar los valores de los campos
        });
    }

    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            ocultarTodo();  

            if (radio.value === 'Tarjeta') {
                camposTarjeta.style.display = 'block';  // Mostrar campos de tarjeta
                camposTarjeta.querySelectorAll('input').forEach(input => input.required = true);
            } else if (radio.value === 'OXXO') {
                mensajeOxxo.style.display = 'block';  // Mostrar mensaje de OXXO
            } else if (radio.value === 'PayPal') {
                mensajePaypal.style.display = 'block';  // Mostrar mensaje de PayPal
            }
        });
    });

    // Validación del formulario de pago
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

    // Eliminar producto del carrito
    document.querySelectorAll('.eliminar').forEach(button => {
    button.addEventListener('click', function () {
            let fila = this.closest('tr');
            let id = fila.dataset.id; // Asegúrate de que la fila tenga un atributo data-id
            fetch(`/eliminar_carrito/${id}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fila.remove(); // Eliminar la fila del carrito
                    if (document.querySelectorAll('#tabla-carrito tbody tr').length === 0) {
                        document.getElementById('carrito-container').innerHTML = '<p id="mensaje-vacio">🛒 El carrito está vacío.</p>';
                    }
                    actualizarTotales(); // Actualizar totales después de eliminar
                } else {
                    alert('Error al eliminar el artículo');
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // Cambiar cantidad en el carrito
    document.querySelectorAll(".cantidad").forEach(input => {
       input.addEventListener("change", function () {
           let id = this.dataset.id;
           let cantidad = this.value;
           fetch(`/actualizar_carrito/${id}`, {
               method: "POST",
               headers: { "Content-Type": "application/json" },
               body: JSON.stringify({ cantidad: cantidad })
           })
           .then(response => response.json())
           .then(data => {
               if (data.total !== undefined) {
                   // Actualizar el total del artículo en la tabla
                   this.closest("tr").querySelector(".total").textContent = `$${data.total.toFixed(2)}`;
                   actualizarTotales(); // Actualizar totales después de cambiar la cantidad
               } else {
                   console.error("Error al actualizar la cantidad:", data.error);
               }
           })
           .catch(error => console.error("Error:", error));
       });
   });
   actualizarTotales();  // Calcular totales al cargar

    // Agregar la lógica de focus y blur para los campos de entrada
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transition = 'transform 0.2s ease'; // Asegurar transición suave
            this.style.transform = 'scale(1.05)'; // Aumentar tamaño al enfocarse
        });

        input.addEventListener('blur', function() {
            this.style.transition = 'transform 0.2s ease'; // Asegurar transición suave
            this.style.transform = 'scale(1)'; // Volver al tamaño normal cuando se pierde el foco
        });
    });
});

   function actualizarTotales() {
       let subtotal = 0;
       document.querySelectorAll('.cantidad').forEach(input => {
           let cantidad = parseInt(input.value);
           let precio = parseFloat(input.getAttribute('data-precio'));
           let total = cantidad * precio;
           input.closest('tr').querySelector('.total').textContent = `$${total.toFixed(2)}`;
           subtotal += total;
       });
       let impuesto = subtotal * 0.16; // Suponiendo un impuesto del 16%
       let totalFinal = subtotal + impuesto;
       document.getElementById('subtotal').textContent = subtotal.toFixed(2);
       document.getElementById('impuesto').textContent = impuesto.toFixed(2);
       document.getElementById('total').textContent = totalFinal.toFixed(2);
   }
document.getElementById('btnProcesar').addEventListener('click', function () {
    const form = document.getElementById('form-pago');
    const formData = new FormData(form);

    // Mostrar modal de carga
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

