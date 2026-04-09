# app/events.py

from typing import Any, Optional

from app.websockets.manager import manager
from app.workers.path_utils import normalize_path
from app.utils.time import now_ms


def emit_job_update(
    *,
    job,
    media_path: Optional[str],
    subtitle_path: Optional[str],
    progress: int,
    engine_result: Optional[Any],
    logs: dict,
    payload: dict,
) -> None:
    event = {
        "event_type": "job_update",
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "progress": progress,
        "media_path": normalize_path(media_path) if media_path else None,
        "subtitle_path": normalize_path(subtitle_path) if subtitle_path else None,
        "engine": (
            getattr(engine_result, "engine_name", None) if engine_result else None
        ),
        "engine_confidence": (
            getattr(engine_result, "confidence", None) if engine_result else None
        ),
        "logs": logs,
        "payload": payload,
        "updated_at": now_ms(),
    }
    manager.broadcast_sync(event)


def emit_hash_audit(
    *,
    path: str,
    old_hash: Optional[str],
    new_hash: Optional[str],
    status: str,
) -> None:
    event = {
        "event_type": "hash_audit",
        "file": normalize_path(path),
        "old_hash": old_hash,
        "new_hash": new_hash,
        "status": status,
        "updated_at": now_ms(),
    }
    manager.broadcast_sync(event)


def emit_hash_error(
    *,
    path: str,
    error: str,
) -> None:
    event = {
        "event_type": "hash_error",
        "file": normalize_path(path),
        "error": error,
        "updated_at": now_ms(),
    }
    manager.broadcast_sync(event)
