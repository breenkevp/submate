// app/dashboard/audits.js

import EventBus from "/dashboard/eventBus.js";

const audits = [];
const MAX_AUDITS = 200;
const ROW_ANIMATION_CLASS = "row-updated";
const MAX_ANIMATION_MS = 600;

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
    if (!ts) return "-";
    return new Date(ts).toLocaleTimeString();
}

function getAuditsTbody() {
    return document.getElementById("auditsBody");
}

function applyRowAnimation(row) {
    row.classList.remove(ROW_ANIMATION_CLASS);
    // force reflow
    // eslint-disable-next-line no-unused-expressions
    row.offsetWidth;
    row.classList.add(ROW_ANIMATION_CLASS);
    setTimeout(() => row.classList.remove(ROW_ANIMATION_CLASS), MAX_ANIMATION_MS);
}

function renderAudits() {
    const tbody = getAuditsTbody();
    tbody.innerHTML = "";

    audits
        .slice() // copy
        .sort((a, b) => b.timestamp - a.timestamp)
        .forEach(a => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td title="${a.file}">${a.file}</td>
                <td title="${a.old_hash || ""}">${a.old_hash || "-"}</td>
                <td title="${a.new_hash || ""}">${a.new_hash || "-"}</td>
                <td>${statusBadge(a.status)}</td>
                <td title="Event time">${formatTime(a.timestamp)}</td>
            `;
            row.style.cursor = "pointer";
            row.addEventListener("click", () => {
                EventBus.publish("audit_row_click", a);
            });
            tbody.appendChild(row);
            applyRowAnimation(row);
        });
}

EventBus.subscribe("hash_audit", (data) => {
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

    renderAudits();
});
