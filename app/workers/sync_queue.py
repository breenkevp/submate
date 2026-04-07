# app/workers/sync_queue.py

import time
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.pairings import Pairing
from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.engines.ffsubsync import run_best_engine, EngineResultData
from app.workers.path_utils import normalize_path

# Adjust this import if your websocket broadcaster is named differently
from app.websockets.manager import manager  # type: ignore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_ms() -> int:
    return int(time.time() * 1000)


def _build_logs(engine_result: Optional[EngineResultData]) -> dict:
    """
    EngineResultData.message currently contains combined stdout+stderr.
    We expose it as logs.engine and leave stdout/stderr empty for now.
    """
    if not engine_result:
        return {"engine": "", "stdout": "", "stderr": ""}

    return {
        "engine": engine_result.message or "",
        "stdout": "",
        "stderr": "",
    }


def _build_payload(job: Job) -> dict:
    return {
        "media_id": job.media_id,
        "subtitle_id": job.subtitle_id,
        "pairing_id": job.pairing_id,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
    }


def _emit_job_update(
    job: Job,
    db: Session,
    *,
    progress: int,
    engine_result: Optional[EngineResultData] = None,
) -> None:
    """
    Emit a hybrid-format job_update event.
    """

    media_path = None
    subtitle_path = None

    if job.media_id:
        media = db.get(MediaFile, job.media_id)
        if media:
            media_path = normalize_path(media.path)

    if job.subtitle_id:
        sub = db.get(SubtitleFile, job.subtitle_id)
        if sub:
            subtitle_path = normalize_path(sub.path)

    event = {
        "event_type": "job_update",
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "progress": progress,
        "media_path": media_path,
        "subtitle_path": subtitle_path,
        "engine": engine_result.engine_name if engine_result else None,
        "engine_confidence": engine_result.confidence if engine_result else None,
        "logs": _build_logs(engine_result),
        "payload": _build_payload(job),
        "updated_at": _now_ms(),
    }

    manager.broadcast(event)


# ---------------------------------------------------------------------------
# Worker Execution
# ---------------------------------------------------------------------------


def process_sync_job(job_id: int) -> None:
    """
    Execute a sync job:
      - load job + media/subtitle
      - emit progress updates
      - run engine
      - update pairing
      - emit final job_update
    """
    db: Session = SessionLocal()

    try:
        job: Optional[Job] = db.get(Job, job_id)
        if not job:
            return

        # Mark job running
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        job.attempts += 1
        db.commit()
        db.refresh(job)

        _emit_job_update(job, db, progress=0)

        # Load media + subtitle
        media = db.get(MediaFile, job.media_id) if job.media_id else None
        sub = db.get(SubtitleFile, job.subtitle_id) if job.subtitle_id else None

        if not media or not sub:
            job.status = "failed"
            job.error_message = "Missing media or subtitle for sync job."
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(job)
            _emit_job_update(job, db, progress=100)
            return

        _emit_job_update(job, db, progress=30)

        # Run engine
        engine_result = run_best_engine(media.path, sub.path)

        _emit_job_update(job, db, progress=70, engine_result=engine_result)

        # Evaluate engine result
        if not engine_result.output_path:
            job.status = "failed"
            job.error_message = engine_result.message or "Engine produced no output."
        else:
            job.status = "completed"

            # Update pairing if present
            pairing = db.get(Pairing, job.pairing_id) if job.pairing_id else None
            if pairing:
                pairing.confidence = engine_result.confidence
                pairing.status = "matched"
                db.add(pairing)

        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        _emit_job_update(job, db, progress=100, engine_result=engine_result)

    except Exception as e:
        # Hard failure
        try:
            job = db.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.finished_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(job)
                _emit_job_update(job, db, progress=100)
        finally:
            pass

    finally:
        db.close()
