function cargarDetalles(pedidoId) {
    fetch(`/api/pedido/${pedidoId}`)
      .then(response => response.json())
      .then(data => {
        let detalleHtml = '';
        data.detalles.forEach(item => {
          detalleHtml += `<tr>
            <td>${item.articulo}</td>
            <td>${item.cantidad}</td>
            <td>$${item.precio}</td>
          </tr>`;
        });
        document.getElementById('detallePedido').innerHTML = detalleHtml;
      });
  }
  

function verDetalleBitacora(pedidoId) {
    fetch(`/bitacora_pedido/${pedidoId}`)
    .then(response => response.json())
    .then(data => {
        let tabla = document.getElementById("bitacoraBody");
        tabla.innerHTML = ""; // Limpiar tabla antes de llenarla

        if (data.length > 0) {
            data.forEach(registro => {
                let fila = `
                    <tr>
                        <td>${registro.fecha}</td>
                        <td>${registro.usuario}</td>
                        <td>${registro.accion}</td>
                    </tr>
                `;
                tabla.innerHTML += fila;
            });
        } else {
            tabla.innerHTML = "<tr><td colspan='3' class='text-center'>No hay registros en la bitácora</td></tr>";
        }

        // Mostrar el modal
        let modal = new bootstrap.Modal(document.getElementById('modalBitacora'));
        modal.show();
    })
    .catch(error => console.error("Error al obtener la bitácora:", error));
}

