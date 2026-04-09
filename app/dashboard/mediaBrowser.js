// app/dashboard/mediaBrowser.js
import EventBus from "/dashboard/eventBus.js";

async function loadMedia() {
    const res = await fetch("/api/media/list");
    const items = await res.json();

    const list = document.getElementById("mediaList");
    list.innerHTML = "";

    items.forEach(item => {
        const li = document.createElement("li");
        li.className = "list-group-item bg-dark text-light";
        li.style.cursor = "pointer";
        li.textContent = item.name;

        li.addEventListener("click", () => {
            EventBus.publish("media_row_click", item);
        });

        list.appendChild(li);
    });
}

document.addEventListener("DOMContentLoaded", loadMedia);
