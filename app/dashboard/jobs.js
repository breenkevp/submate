// dashboard/jobs.js

import EventBus from "/dashboard/eventBus.js";

const jobs = {}; // in-memory job store

function statusBadge(status) {
    const map = {
        queued: "secondary",
        running: "info",
        done: "success",
        failed: "danger"
    };
    const color = map[status] || "secondary";
    return `<span class="badge bg-${color}">${status}</span>`;
}

function renderJobs() {
    const tbody = document.getElementById("jobsBody");
    tbody.innerHTML = "";

    Object.values(jobs)
        .sort((a, b) => b.updated_at - a.updated_at)
        .forEach(job => {
            const row = `
                <tr>
                    <td>${job.id}</td>
                    <td>${job.job_type}</td>
                    <td>${statusBadge(job.status)}</td>
                    <td>${job.progress || 0}%</td>
                    <td>${new Date(job.updated_at).toLocaleTimeString()}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
}

// Subscribe to job updates
EventBus.subscribe("job_update", (data) => {
    jobs[data.id] = {
        id: data.id,
        job_type: data.job_type,
        status: data.status,
        progress: data.progress,
        updated_at: Date.now()
    };

    renderJobs();
});
