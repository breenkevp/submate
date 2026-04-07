// app/dashboard/audits.js

import EventBus from "/dashboard/eventBus.js";

const audits = [];

function statusBadge(status) {
    const map = {
        "match": "success",
        "mismatch": "danger",
        "missing": "warning"
    };
    const color = map[status] || "secondary";
    return `<span class="badge bg-${color}">${status}</span>`;
}

function renderAudits() {
    const tbody = document.getElementById("auditsBody");
    tbody.innerHTML = "";

    audits
        .sort((a, b) => b.timestamp - a.timestamp)
        .forEach(a => {
            const row = `
                <tr>
                    <td>${a.file}</td>
                    <td>${a.old_hash || "-"}</td>
                    <td>${a.new_hash || "-"}</td>
                    <td>${statusBadge(a.status)}</td>
                    <td>${new Date(a.timestamp).toLocaleTimeString()}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
}

EventBus.subscribe("hash_audit", (data) => {
    audits.push({
        file: data.file,
        old_hash: data.old_hash,
        new_hash: data.new_hash,
        status: data.status,
        timestamp: Date.now()
    });

    renderAudits();
});
