# app/main.py

from fastapi import FastAPI
from fastapi.routing import APIRouter
from app.api import ws
from app.api.router import api_router
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="SubMate API",
    description="Media + Subtitle Intelligence Engine",
    version="0.1.0",
)

app.include_router(api_router)
app.include_router(ws.router)

app.mount("/dashboard", StaticFiles(directory="app/dashboard"), name="dashboard")


@app.get("/")
def dashboard():
    return FileResponse("app/dashboard/index.html")
