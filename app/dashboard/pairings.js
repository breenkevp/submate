// app/dashboard/pairings.js

import EventBus from "/dashboard/eventBus.js";

const pairings = {}; // keyed by media_path
const ROW_ANIMATION_CLASS = "row-updated";
const MAX_ANIMATION_MS = 600;

function confidenceBadge(score) {
    const value = typeof score === "number" ? score : 0;
    const pct = (value * 100).toFixed(0);
    let color = "danger";
    if (value >= 0.9) color = "success";
    else if (value >= 0.7) color = "info";
    else if (value >= 0.4) color = "warning";

    return `<span class="badge bg-${color}" title="Confidence: ${pct}%">${pct}%</span>`;
}

function formatTime(ts) {
    if (!ts) return "-";
    return new Date(ts).toLocaleTimeString();
}

function getPairingsTbody() {
    return document.getElementById("pairingsBody");
}

function getOrCreateRow(key) {
    const tbody = getPairingsTbody();
    let row = tbody.querySelector(`tr[data-pairing-key="${CSS.escape(key)}"]`);
    if (!row) {
        row = document.createElement("tr");
        row.dataset.pairingKey = key;
        row.style.cursor = "pointer";
        row.addEventListener("click", () => {
            const pairing = pairings[key];
            if (pairing) {
                EventBus.publish("pairing_row_click", pairing);
            }
        });
        tbody.appendChild(row);
    }
    return row;
}

function applyRowAnimation(row) {
    row.classList.remove(ROW_ANIMATION_CLASS);
    // force reflow
    // eslint-disable-next-line no-unused-expressions
    row.offsetWidth;
    row.classList.add(ROW_ANIMATION_CLASS);
    setTimeout(() => row.classList.remove(ROW_ANIMATION_CLASS), MAX_ANIMATION_MS);
}

function renderPairingRow(p) {
    const key = p.media_path || p.media_name || `pairing-${p.updated_at || Date.now()}`;
    const row = getOrCreateRow(key);
    row.innerHTML = `
        <td title="${p.media_path || ""}">${p.media_name || "-"}</td>
        <td title="${p.subtitle_path || ""}">${p.subtitle_name || "-"}</td>
        <td>${confidenceBadge(p.confidence)}</td>
        <td title="Engine">${p.engine || "-"}</td>
        <td title="Last update">${formatTime(p.updated_at)}</td>
    `;
    applyRowAnimation(row);
}

function sortPairingRows() {
    const tbody = getPairingsTbody();
    const rows = Array.from(tbody.querySelectorAll("tr"));
    rows.sort((a, b) => {
        const aKey = a.dataset.pairingKey;
        const bKey = b.dataset.pairingKey;
        const aP = pairings[aKey];
        const bP = pairings[bKey];
        const aTs = aP?.updated_at || 0;
        const bTs = bP?.updated_at || 0;
        return bTs - aTs;
    });
    rows.forEach(row => tbody.appendChild(row));
}

EventBus.subscribe("pairing_update", (data) => {
    const key = data.media_path || data.media_name;
    if (!key) return;

    pairings[key] = {
        media_path: data.media_path,
        subtitle_path: data.subtitle_path,
        media_name: data.media_name || (data.media_path ? data.media_path.split("/").pop() : "-"),
        subtitle_name: data.subtitle_name || (data.subtitle_path ? data.subtitle_path.split("/").pop() : "-"),
        confidence: typeof data.confidence === "number" ? data.confidence : 0,
        engine: data.engine || "unknown",
        updated_at: data.updated_at || Date.now()
    };

    renderPairingRow(pairings[key]);
    sortPairingRows();
});
