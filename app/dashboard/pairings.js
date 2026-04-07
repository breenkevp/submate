// app/dashboard/pairings.js

import EventBus from "/dashboard/eventBus.js";

const pairings = {};

function confidenceBadge(score) {
    if (score >= 0.9) return `<span class="badge bg-success">${(score * 100).toFixed(0)}%</span>`;
    if (score >= 0.7) return `<span class="badge bg-info">${(score * 100).toFixed(0)}%</span>`;
    if (score >= 0.4) return `<span class="badge bg-warning">${(score * 100).toFixed(0)}%</span>`;
    return `<span class="badge bg-danger">${(score * 100).toFixed(0)}%</span>`;
}

function renderPairings() {
    const tbody = document.getElementById("pairingsBody");
    tbody.innerHTML = "";

    Object.values(pairings)
        .sort((a, b) => b.updated_at - a.updated_at)
        .forEach(p => {
            const row = `
                <tr>
                    <td>${p.media_name}</td>
                    <td>${p.subtitle_name}</td>
                    <td>${confidenceBadge(p.confidence)}</td>
                    <td>${p.engine}</td>
                    <td>${new Date(p.updated_at).toLocaleTimeString()}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
}

EventBus.subscribe("pairing_update", (data) => {
    pairings[data.media_path] = {
        media_name: data.media_name,
        subtitle_name: data.subtitle_name,
        confidence: data.confidence,
        engine: data.engine,
        updated_at: Date.now()
    };

    renderPairings();
});
