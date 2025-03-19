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