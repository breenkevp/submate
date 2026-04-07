// app/dashboard/jobs.js

import EventBus from "/dashboard/eventBus.js";

const jobs = {}; // in-memory job store
const ROW_ANIMATION_CLASS = "row-updated";
const MAX_ANIMATION_MS = 600;

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
    const value = typeof progress === "number" ? progress : 0;
    const clamped = Math.max(0, Math.min(100, value));
    return `
        <div class="progress" style="height: 8px;">
            <div 
                class="progress-bar" 
                role="progressbar" 
                style="width: ${clamped}%;"
                aria-valuenow="${clamped}" 
                aria-valuemin="0" 
                aria-valuemax="100"
                title="${clamped}% complete">
            </div>
        </div>
    `;
}

function formatTime(ts) {
    if (!ts) return "-";
    return new Date(ts).toLocaleTimeString();
}

function getJobsTbody() {
    return document.getElementById("jobsBody");
}

function getOrCreateRow(jobId) {
    const tbody = getJobsTbody();
    let row = tbody.querySelector(`tr[data-job-id="${jobId}"]`);
    if (!row) {
        row = document.createElement("tr");
        row.dataset.jobId = jobId;
        row.style.cursor = "pointer";
        row.addEventListener("click", () => {
            const job = jobs[jobId];
            if (job) {
                EventBus.publish("job_row_click", job);
            }
        });
        tbody.appendChild(row);
    }
    return row;
}

function applyRowAnimation(row) {
    row.classList.remove(ROW_ANIMATION_CLASS);
    // force reflow to restart animation
    // eslint-disable-next-line no-unused-expressions
    row.offsetWidth;
    row.classList.add(ROW_ANIMATION_CLASS);
    setTimeout(() => row.classList.remove(ROW_ANIMATION_CLASS), MAX_ANIMATION_MS);
}

function renderJobRow(job) {
    const row = getOrCreateRow(job.id);
    row.innerHTML = `
        <td title="Job ID">${job.id}</td>
        <td title="Job type">${job.job_type || "-"}</td>
        <td>${statusBadge(job.status)}</td>
        <td>${progressBar(job.progress)}</td>
        <td title="Last update">${formatTime(job.updated_at)}</td>
    `;
    applyRowAnimation(row);
}

function sortJobRows() {
    const tbody = getJobsTbody();
    const rows = Array.from(tbody.querySelectorAll("tr"));
    rows.sort((a, b) => {
        const aId = a.dataset.jobId;
        const bId = b.dataset.jobId;
        const aJob = jobs[aId];
        const bJob = jobs[bId];
        const aTs = aJob?.updated_at || 0;
        const bTs = bJob?.updated_at || 0;
        return bTs - aTs;
    });
    rows.forEach(row => tbody.appendChild(row));
}

// Subscribe to job updates
EventBus.subscribe("job_update", (data) => {
    const id = data.id;
    if (!id) return;

    jobs[id] = {
        id,
        job_type: data.job_type || data.type || "unknown",
        status: data.status || "queued",
        progress: typeof data.progress === "number" ? data.progress : 0,
        updated_at: data.updated_at || Date.now()
    };

    renderJobRow(jobs[id]);
    sortJobRows();
});
