function filtrarTabla() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let table = document.getElementById("tablaArticulos");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) { 
        let firstCell = rows[i].getElementsByTagName("td")[0]; 
        if (firstCell) {
            let idTexto = firstCell.textContent || firstCell.innerText;
            rows[i].style.display = idTexto.toLowerCase().includes(input) ? "" : "none";
        }
    }
}