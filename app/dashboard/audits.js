// app/dashboard/audits.js

import EventBus from "/dashboard/eventBus.js";

const audits = [];
const MAX_AUDITS = 200;
const FLASH_CLASS = "row-updated";
const FLASH_MS = 600;

function statusBadge(status) {
    const map = {
        match: "success",
        mismatch: "danger",
        missing: "warning"
    };
    const color = map[status] || "secondary";
    return `<span class="badge bg-${color}" title="Status: ${status}">${status}</span>`;
}

function formatTime(ts) {
    return ts ? new Date(ts).toLocaleTimeString() : "-";
}

function tbody() {
    return document.getElementById("auditsBody");
}

function flash(row) {
    row.classList.remove(FLASH_CLASS);
    row.offsetWidth;
    row.classList.add(FLASH_CLASS);
    setTimeout(() => row.classList.remove(FLASH_CLASS), FLASH_MS);
}

function render() {
    const body = tbody();
    body.innerHTML = "";

    audits
        .slice()
        .sort((a, b) => b.timestamp - a.timestamp)
        .forEach(a => {
            const row = document.createElement("tr");
            row.style.cursor = "pointer";
            row.innerHTML = `
                <td title="${a.file}">${a.file}</td>
                <td title="${a.old_hash || ""}">${a.old_hash || "-"}</td>
                <td title="${a.new_hash || ""}">${a.new_hash || "-"}</td>
                <td>${statusBadge(a.status)}</td>
                <td>${formatTime(a.timestamp)}</td>
            `;
            row.addEventListener("click", () => EventBus.publish("audit_row_click", a));
            body.appendChild(row);
            flash(row);
        });
}

EventBus.subscribe("hash_audit", data => {
    audits.push({
        file: data.file,
        old_hash: data.old_hash,
        new_hash: data.new_hash,
        status: data.status || "match",
        timestamp: data.timestamp || Date.now()
    });

    if (audits.length > MAX_AUDITS) {
        audits.splice(0, audits.length - MAX_AUDITS);
    }

    render();
});
