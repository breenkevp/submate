// app/dashboard/detailsPanel.js

import EventBus from "/dashboard/eventBus.js";

let currentItem = null;
let currentType = null;

function el(id) {
    return document.getElementById(id);
}

function setText(id, text) {
    const node = el(id);
    if (node) node.textContent = text || "";
}

function setHtml(id, html) {
    const node = el(id);
    if (node) node.innerHTML = html || "";
}

function showElement(id) {
    const node = el(id);
    if (node) node.style.display = "";
}

function hideElement(id) {
    const node = el(id);
    if (node) node.style.display = "none";
}

function formatTimestamp(ts) {
    if (!ts) return "-";
    return new Date(ts).toLocaleString();
}

function renderMetadata() {
    if (!currentItem || !currentType) {
        setHtml("detailsMetadata", "<span class='text-muted'>Select a row to see details.</span>");
        return;
    }

    let html = "<dl class='row mb-0'>";

    if (currentType === "job") {
        html += `
            <dt class="col-4">Job ID</dt><dd class="col-8">${currentItem.id}</dd>
            <dt class="col-4">Type</dt><dd class="col-8">${currentItem.job_type}</dd>
            <dt class="col-4">Status</dt><dd class="col-8">${currentItem.status}</dd>
            <dt class="col-4">Progress</dt><dd class="col-8">${currentItem.progress || 0}%</dd>
            <dt class="col-4">Updated</dt><dd class="col-8">${formatTimestamp(currentItem.updated_at)}</dd>
        `;
    } else if (currentType === "pairing") {
        html += `
            <dt class="col-4">Media</dt><dd class="col-8">${currentItem.media_name}</dd>
            <dt class="col-4">Subtitle</dt><dd class="col-8">${currentItem.subtitle_name}</dd>
            <dt class="col-4">Confidence</dt><dd class="col-8">${((currentItem.confidence || 0) * 100).toFixed(0)}%</dd>
            <dt class="col-4">Engine</dt><dd class="col-8">${currentItem.engine}</dd>
            <dt class="col-4">Updated</dt><dd class="col-8">${formatTimestamp(currentItem.updated_at)}</dd>
        `;
    } else if (currentType === "audit") {
        html += `
            <dt class="col-4">File</dt><dd class="col-8">${currentItem.file}</dd>
            <dt class="col-4">Old hash</dt><dd class="col-8">${currentItem.old_hash || "-"}</dd>
            <dt class="col-4">New hash</dt><dd class="col-8">${currentItem.new_hash || "-"}</dd>
            <dt class="col-4">Status</dt><dd class="col-8">${currentItem.status}</dd>
            <dt class="col-4">Time</dt><dd class="col-8">${formatTimestamp(currentItem.timestamp)}</dd>
        `;
    }

    html += "</dl>";
    setHtml("detailsMetadata", html);
}

function renderEngineInfo() {
    if (!currentItem || !currentType) {
        setHtml("detailsEngine", "");
        return;
    }

    let html = "";

    if (currentType === "job") {
        // Placeholder for future engine/job info
        if (currentItem.engine) {
            html += `<div><strong>Engine:</strong> ${currentItem.engine}</div>`;
        }
        if (currentItem.worker_id) {
            html += `<div><strong>Worker:</strong> ${currentItem.worker_id}</div>`;
        }
    } else if (currentType === "pairing") {
        html += `<div><strong>Engine:</strong> ${currentItem.engine}</div>`;
        if (currentItem.engine_reason) {
            html += `<div><strong>Reason:</strong> ${currentItem.engine_reason}</div>`;
        }
    } else if (currentType === "audit") {
        // audits may not have engine info
    }

    setHtml("detailsEngine", html);
}

function renderLogs() {
    const logsEl = el("detailsLogs");
    if (!logsEl) return;

    if (!currentItem) {
        logsEl.textContent = "";
        return;
    }

    // Look for likely log fields
    const logs =
        currentItem.engine_logs ||
        currentItem.logs ||
        currentItem.stdout ||
        currentItem.stderr ||
        null;

    if (!logs) {
        logsEl.textContent = "No logs available for this item.";
        return;
    }

    logsEl.textContent = Array.isArray(logs) ? logs.join("\n") : String(logs);
}

function renderJson() {
    const jsonEl = el("detailsJson");
    if (!jsonEl) return;

    if (!currentItem) {
        jsonEl.textContent = "";
        return;
    }

    jsonEl.textContent = JSON.stringify(currentItem, null, 2);
}

function setTitleAndSubtitle() {
    if (!currentItem || !currentType) {
        setText("detailsTitle", "Details");
        setText("detailsSubtitle", "");
        return;
    }

    if (currentType === "job") {
        setText("detailsTitle", "Job details");
        setText("detailsSubtitle", `Job ${currentItem.id}`);
    } else if (currentType === "pairing") {
        setText("detailsTitle", "Pairing details");
        setText("detailsSubtitle", currentItem.media_name || currentItem.media_path || "");
    } else if (currentType === "audit") {
        setText("detailsTitle", "Audit details");
        setText("detailsSubtitle", currentItem.file || "");
    }
}

function selectItem(type, item) {
    currentType = type;
    currentItem = item;

    setTitleAndSubtitle();
    renderMetadata();
    renderEngineInfo();
    renderLogs();
    renderJson();
}

function setupToggles() {
    const logsToggle = el("detailsLogsToggle");
    const logsEl = el("detailsLogs");
    const jsonToggle = el("detailsJsonToggle");
    const jsonEl = el("detailsJson");

    if (logsToggle && logsEl) {
        logsToggle.addEventListener("click", () => {
            const isHidden = logsEl.style.display === "none" || logsEl.style.display === "";
            if (isHidden) {
                showElement("detailsLogs");
                logsToggle.textContent = "Hide logs";
            } else {
                hideElement("detailsLogs");
                logsToggle.textContent = "Show logs";
            }
        });
    }

    if (jsonToggle && jsonEl) {
        jsonToggle.addEventListener("click", () => {
            const isHidden = jsonEl.style.display === "none" || jsonEl.style.display === "";
            if (isHidden) {
                showElement("detailsJson");
                jsonToggle.textContent = "Hide raw JSON";
            } else {
                hideElement("detailsJson");
                jsonToggle.textContent = "Show raw JSON";
            }
        });
    }
}

function init() {
    setupToggles();
    renderMetadata(); // initial "select a row" message

    EventBus.subscribe("job_row_click", job => {
        selectItem("job", job);
    });

    EventBus.subscribe("pairing_row_click", pairing => {
        selectItem("pairing", pairing);
    });

    EventBus.subscribe("audit_row_click", audit => {
        selectItem("audit", audit);
    });

    EventBus.subscribe("media_row_click", media => {
    selectItem("media", media);
});

}

document.addEventListener("DOMContentLoaded", init);
