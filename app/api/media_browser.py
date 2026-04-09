# app/api/media_browser.py
from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

MEDIA_ROOT = Path("/media")  # adjust to your mount


@router.get("/media/list")
def list_media():
    items = []
    for path in MEDIA_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".mkv", ".mp4", ".avi"}:
            items.append(
                {"path": str(path), "name": path.name, "dir": str(path.parent)}
            )
    return items
