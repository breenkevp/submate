# app/scanner/classifier.py

from pathlib import Path

MEDIA_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}
SUBTITLE_EXTENSIONS = {".srt", ".ass", ".vtt"}


def classify_file(path: str) -> str | None:
    """
    Classify a file as 'media', 'subtitle', or None.

    Args:
        path: Full file path.

    Returns:
        "media", "subtitle", or None.
    """
    ext = Path(path).suffix.lower()

    if ext in MEDIA_EXTENSIONS:
        return "media"

    if ext in SUBTITLE_EXTENSIONS:
        return "subtitle"

    return None
