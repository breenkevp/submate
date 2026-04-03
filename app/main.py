# app/main.py

from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="SubMate API",
    description="Media + Subtitle Intelligence Engine",
    version="0.1.0",
)

app.include_router(api_router)
