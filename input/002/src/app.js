const API_URL = "data.json";

let data = [];
let filterText = "";
let sortColumn = null;
let sortAsc = true;

async function loadData() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error("Faili ei õnnestunud lugeda");
        data = await response.json();
        renderTable();
    } catch (error) {
        document.getElementById("error-message").textContent =
            "Andmete laadimine ebaõnnestus: " + error.message;
    }
}

function renderTable() {
    const tbody = document.querySelector("#data-table tbody");
    tbody.innerHTML = "";

    let filtered = data.filter((item) => {
        const search = filterText.toLowerCase();
        return (
            item.name.toLowerCase().includes(search) ||
            item.category.toLowerCase().includes(search)
        );
    });

    if (sortColumn) {
        filtered.sort((a, b) => {
            const valA = a[sortColumn];
            const valB = b[sortColumn];
            if (valA < valB) return sortAsc ? -1 : 1;
            if (valA > valB) return sortAsc ? 1 : -1;
            return 0;
        });
    }

    filtered.forEach((item) => {
        const row = tbody.insertRow();
        row.insertCell().textContent = item.name;
        row.insertCell().textContent = item.category;
        row.insertCell().textContent = item.price + " €";
        row.insertCell().textContent = item.quantity;
    });
}

document.getElementById("filter-input").addEventListener("input", (e) => {
    filterText = e.target.value;
    renderTable();
});

document.querySelectorAll("#data-table th").forEach((th) => {
    th.addEventListener("click", () => {
        const column = th.dataset.column;
        if (sortColumn === column) {
            sortAsc = !sortAsc;
        } else {
            sortColumn = column;
            sortAsc = true;
        }
        renderTable();
    });
});

loadData();
