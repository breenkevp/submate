# app/api/router.py

from fastapi import APIRouter
from app.api import media, media_browser, subtitles, pairings, audits, jobs, scan, ws

api_router = APIRouter()

api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(subtitles.router, prefix="/subtitles", tags=["Subtitles"])
api_router.include_router(pairings.router, prefix="/pairings", tags=["Pairings"])
api_router.include_router(audits.router, prefix="/audits", tags=["Audits"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(scan.router, prefix="/scan", tags=["Scan"])
api_router.include_router(media_browser.router, prefix="/api", tags=["Media Browser"])

# WebSocket routes are mounted directly on app in main.py, see below
api_router.include_router(ws.router, tags=["WebSocket"])
