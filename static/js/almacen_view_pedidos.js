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