function filtrarTabla() {
    var input = document.getElementById("searchInput").value.toLowerCase();
    var rows = document.querySelectorAll("#tablaArticulos tbody tr");

    rows.forEach(row => {
        var idArticulo = row.cells[0].innerText.toLowerCase();
        row.style.display = idArticulo.includes(input) ? "" : "none";
    });
}
function actualizarExistencia(articuloId) {
    let nuevaExistencia = document.getElementById(`nuevaExistencia-${articuloId}`).value;

    // Validación de entrada
    if (nuevaExistencia === "" || isNaN(nuevaExistencia) || nuevaExistencia < 0) {
        alert("Ingrese un número válido para la existencia.");
        return;
    }

    // Enviar solicitud AJAX al servidor
    fetch('/actualizar_existencia', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: articuloId, existencia: parseInt(nuevaExistencia) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`existencia-${articuloId}`).textContent = nuevaExistencia;
            alert("Existencia actualizada correctamente.");
        } else {
            alert("Error al actualizar existencia.");
        }
    })
    .catch(error => console.error("Error:", error));
}
