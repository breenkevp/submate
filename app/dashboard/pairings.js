// app/dashboard/pairings.js

import EventBus from "/dashboard/eventBus.js";

const pairings = {};
const FLASH_CLASS = "row-updated";
const FLASH_MS = 600;

function confidenceBadge(score) {
    const pct = ((score || 0) * 100).toFixed(0);
    let color = "danger";
    if (score >= 0.9) color = "success";
    else if (score >= 0.7) color = "info";
    else if (score >= 0.4) color = "warning";

    return `<span class="badge bg-${color}" title="Confidence: ${pct}%">${pct}%</span>`;
}

function formatTime(ts) {
    return ts ? new Date(ts).toLocaleTimeString() : "-";
}

function tbody() {
    return document.getElementById("pairingsBody");
}

function getOrCreateRow(key) {
    let row = tbody().querySelector(`tr[data-pairing-key="${CSS.escape(key)}"]`);
    if (!row) {
        row = document.createElement("tr");
        row.dataset.pairingKey = key;
        row.style.cursor = "pointer";
        row.addEventListener("click", () => EventBus.publish("pairing_row_click", pairings[key]));
        tbody().appendChild(row);
    }
    return row;
}

function flash(row) {
    row.classList.remove(FLASH_CLASS);
    row.offsetWidth;
    row.classList.add(FLASH_CLASS);
    setTimeout(() => row.classList.remove(FLASH_CLASS), FLASH_MS);
}

function renderRow(p) {
    const row = getOrCreateRow(p.media_path);
    row.innerHTML = `
        <td title="${p.media_path}">${p.media_name}</td>
        <td title="${p.subtitle_path}">${p.subtitle_name}</td>
        <td>${confidenceBadge(p.confidence)}</td>
        <td title="Engine">${p.engine}</td>
        <td>${formatTime(p.updated_at)}</td>
    `;
    flash(row);
}

function sortRows() {
    const rows = Array.from(tbody().querySelectorAll("tr"));
    rows.sort((a, b) => {
        const pa = pairings[a.dataset.pairingKey]?.updated_at || 0;
        const pb = pairings[b.dataset.pairingKey]?.updated_at || 0;
        return pb - pa;
    });
    rows.forEach(r => tbody().appendChild(r));
}

EventBus.subscribe("pairing_update", data => {
    const key = data.media_path;
    if (!key) return;

    pairings[key] = {
        media_path: data.media_path,
        subtitle_path: data.subtitle_path,
        media_name: data.media_name || data.media_path.split("/").pop(),
        subtitle_name: data.subtitle_name || data.subtitle_path.split("/").pop(),
        confidence: data.confidence || 0,
        engine: data.engine || "unknown",
        updated_at: data.updated_at || Date.now()
    };

    renderRow(pairings[key]);
    sortRows();
});
