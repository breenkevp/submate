# app/api/router.py

from fastapi import APIRouter
from app.api import media, subtitles, pairings, audits, jobs, scan

api_router = APIRouter()

api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(subtitles.router, prefix="/subtitles", tags=["Subtitles"])
api_router.include_router(pairings.router, prefix="/pairings", tags=["Pairings"])
api_router.include_router(audits.router, prefix="/audits", tags=["Audits"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(scan.router, prefix="/scan", tags=["Scan"])
