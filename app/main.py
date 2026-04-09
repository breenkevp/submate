# app/main.py
import subprocess
import requests

from fastapi import FastAPI
from fastapi.routing import APIRouter
from app.api.router import api_router
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


router = APIRouter()

worker_process = None

app = FastAPI(
    title="SubMate API",
    description="Media + Subtitle Intelligence Engine",
    version="0.1.0",
)

app.include_router(api_router)
app.include_router(router)

app.mount("/dashboard", StaticFiles(directory="app/dashboard"), name="dashboard")


@app.get("/")
def dashboard():
    return FileResponse("app/dashboard/index.html")


@router.post("/api/start-worker")
def start_worker():
    global worker_process
    if worker_process and worker_process.poll() is None:
        return {"status": "already_running"}

    worker_process = subprocess.Popen(
        ["python", "-m", "app.workers.worker"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {"status": "started"}


@router.post("/api/stop-worker")
def stop_worker():
    global worker_process
    if worker_process and worker_process.poll() is None:
        worker_process.terminate()
        return {"status": "stopped"}
    return {"status": "not_running"}


@router.post("/api/run-scan")
def run_scan():
    requests.post("http://localhost:9090/api/scan")
    return {"status": "scan_triggered"}
