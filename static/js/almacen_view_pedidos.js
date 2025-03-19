function gestionarPedido(ventaId, accion) {
    fetch(`/gestionar_pedido/${ventaId}/${accion}`, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje);
        location.reload();
    })
    .catch(error => console.error("Error:", error));
}
function verDetalles(ventaId) {
    fetch(`/obtener_detalles/${ventaId}`)
        .then(response => response.json())
        .then(data => {
            console.log("Detalles de la venta:", data);

            // Limpiar la tabla antes de agregar nuevos datos
            let tablaBody = document.getElementById("detallesVentaBody");
            tablaBody.innerHTML = "";

            // Insertar cada producto en la tabla
            data.forEach(item => {
                let fila = `
                    <tr>
                        <td>${item.producto}</td>
                        <td>${item.cantidad}</td>
                        <td>$${item.precio.toFixed(2)}</td>
                    </tr>`;
                tablaBody.innerHTML += fila;
            });

            // Mostrar el modal
            let modal = new bootstrap.Modal(document.getElementById('detallesVentaModal'));
            modal.show();
        })
        .catch(error => console.error("Error al obtener detalles:", error));
}
function gestionarPedido(ventaId, accion) {
    if (accion === 'Aceptar') {
        fetch('/finalizar_pedido', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                venta_id: ventaId,
                usuario_id: 1  // Reemplázalo con el ID real del usuario logueado
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.mensaje) {
                alert(data.mensaje);
                location.reload(); // Recargar la página para reflejar cambios
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error al procesar el pedido:", error));
    }
}
