document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("my-table");
    const details = document.getElementById("details");
    const container = document.getElementById("extended");
    const close_button = document.getElementById("close");

    table.addEventListener("click", function (event) {
        const row = event.target.closest("tr");
        if (!row || !row.dataset.name) return;

        const name = encodeURIComponent(row.dataset.name);

        fetch(`/details/${name}`)
            .then(res => res.json())
            .then(data => {
                details.innerHTML = `
                    <p>${data}</p>
                `;
                container.classList.add("Visable");
            })
            .catch(err => console.error("Failed to load details:", err));
    });

    close_button.addEventListener("click", function (event) {
        container.classList.remove("Visable");
    });

});