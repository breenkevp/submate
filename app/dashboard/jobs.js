// app/dashboard/jobs.js

import EventBus from "/dashboard/eventBus.js";

const jobs = {}; 
const FLASH_CLASS = "row-updated";
const FLASH_MS = 600;

function statusBadge(status) {
    const map = {
        queued: "secondary",
        running: "info",
        done: "success",
        failed: "danger"
    };
    const color = map[status] || "secondary";
    return `<span class="badge bg-${color}" title="Status: ${status}">${status}</span>`;
}

function progressBar(progress) {
    const pct = Math.max(0, Math.min(100, progress || 0));
    return `
        <div class="progress" style="height: 8px;">
            <div class="progress-bar" role="progressbar"
                 style="width: ${pct}%;" 
                 aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"
                 title="${pct}% complete">
            </div>
        </div>
    `;
}

function formatTime(ts) {
    return ts ? new Date(ts).toLocaleTimeString() : "-";
}

function tbody() {
    return document.getElementById("jobsBody");
}

function getOrCreateRow(id) {
    let row = tbody().querySelector(`tr[data-job-id="${id}"]`);
    if (!row) {
        row = document.createElement("tr");
        row.dataset.jobId = id;
        row.style.cursor = "pointer";
        row.addEventListener("click", () => EventBus.publish("job_row_click", jobs[id]));
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

function renderRow(job) {
    const row = getOrCreateRow(job.id);
    row.innerHTML = `
        <td>${job.id}</td>
        <td title="Job type">${job.job_type}</td>
        <td>${statusBadge(job.status)}</td>
        <td>${progressBar(job.progress)}</td>
        <td>${formatTime(job.updated_at)}</td>
    `;
    flash(row);
}

function sortRows() {
    const rows = Array.from(tbody().querySelectorAll("tr"));
    rows.sort((a, b) => {
        const ja = jobs[a.dataset.jobId]?.updated_at || 0;
        const jb = jobs[b.dataset.jobId]?.updated_at || 0;
        return jb - ja;
    });
    rows.forEach(r => tbody().appendChild(r));
}

EventBus.subscribe("job_update", data => {
    jobs[data.id] = {
        id: data.id,
        job_type: data.job_type || "unknown",
        status: data.status || "queued",
        progress: data.progress || 0,
        updated_at: data.updated_at || Date.now()
    };

    renderRow(jobs[data.id]);
    sortRows();
});
