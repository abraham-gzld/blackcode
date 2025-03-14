
document.querySelectorAll(".cantidad").forEach(input => {
    input.addEventListener("change", function() {
        let id = this.dataset.id;
        let cantidad = this.value;

        fetch(`/actualizar_carrito/${id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cantidad: cantidad })
        })
        .then(response => response.json())
        .then(data => {
            this.closest("tr").querySelector(".total").textContent = `$${data.total}`;
        })
        .catch(error => console.error("Error:", error));
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

    let impuesto = subtotal * 0.16;
    let totalFinal = subtotal + impuesto;

    document.getElementById('subtotal').textContent = subtotal.toFixed(2);
    document.getElementById('impuesto').textContent = impuesto.toFixed(2);
    document.getElementById('total').textContent = totalFinal.toFixed(2);
}

document.querySelectorAll('.cantidad').forEach(input => {
    input.addEventListener('change', function() {
        if (this.value > 10) this.value = 10;
        if (this.value < 1) this.value = 1;
        actualizarTotales();
    });
});

document.querySelectorAll('.eliminar').forEach(button => {
    button.addEventListener('click', function() {
        let fila = this.closest('tr');
        fila.remove();

        if (document.querySelectorAll('#tabla-carrito tbody tr').length === 0) {
            document.getElementById('carrito-container').innerHTML = '<p id="mensaje-vacio">🛒 El carrito está vacío.</p>';
        }

        actualizarTotales();
    });
});

actualizarTotales();

document.addEventListener("DOMContentLoaded", function () {
const botonPago = document.querySelector(".btn-success");  // Selecciona el botón de pago

if (botonPago) {
botonPago.addEventListener("click", function () {
    fetch("/procesar_pago", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);  // Mostrar mensaje de éxito
            window.location.href = "/cliente";  // Redirigir a la tienda
        } else {
            alert("Error: " + data.message);  // Mostrar error
        }
    })
    .catch(error => {
        console.error("Error en la petición:", error);
        alert("Hubo un problema al procesar el pago.");
    });
});
}
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".eliminar").forEach((button) => {
        button.addEventListener("click", function () {
            let fila = this.closest("tr"); // Obtener la fila del producto
            let id = fila.getAttribute("data-id"); // Obtener el ID del producto

            fetch(`/eliminar_carrito/${id}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fila.remove(); // Eliminar la fila de la tabla
                    actualizarResumen(); // Actualizar los totales del carrito
                }
            })
            .catch(error => console.error("Error al eliminar producto:", error));
        });
    });

    function actualizarResumen() {
        let subtotal = 0;

        document.querySelectorAll("#tabla-carrito tbody tr").forEach((fila) => {
            let precio = parseFloat(fila.querySelector(".cantidad").getAttribute("data-precio"));
            let cantidad = parseInt(fila.querySelector(".cantidad").value);
            subtotal += precio * cantidad;
        });

        let impuesto = subtotal * 0.16;
        let total = subtotal + impuesto;

        document.getElementById("subtotal").textContent = subtotal.toFixed(2);
        document.getElementById("impuesto").textContent = impuesto.toFixed(2);
        document.getElementById("total").textContent = total.toFixed(2);

        // Mostrar mensaje si el carrito está vacío
        if (subtotal === 0) {
            document.getElementById("tabla-carrito").innerHTML = "";
            document.getElementById("mensaje-vacio").style.display = "block";
        }
    }
});

