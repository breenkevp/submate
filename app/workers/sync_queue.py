# app/workers/sync_queue.py

from typing import Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.pairings import Pairing
from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.engines.ffsubsync import run_best_engine, EngineResultData
from app.events import emit_job_update
from app.utils.time import now_utc


def _build_logs(engine_result: Optional[EngineResultData]) -> dict:
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


def _emit(
    db: Session,
    job: Job,
    *,
    progress: int,
    engine_result: Optional[EngineResultData] = None,
) -> None:
    media_path = None
    subtitle_path = None

    if job.media_id:
        media = db.get(MediaFile, job.media_id)
        if media:
            media_path = media.path

    if job.subtitle_id:
        sub = db.get(SubtitleFile, job.subtitle_id)
        if sub:
            subtitle_path = sub.path

    emit_job_update(
        job=job,
        media_path=media_path,
        subtitle_path=subtitle_path,
        progress=progress,
        engine_result=engine_result,
        logs=_build_logs(engine_result),
        payload=_build_payload(job),
    )


def process_sync_job(job_id: int) -> None:
    db: Session = SessionLocal()

    try:
        job: Optional[Job] = db.get(Job, job_id)
        if not job:
            return

        job.status = "running"
        job.started_at = now_utc()
        job.attempts += 1
        db.commit()
        db.refresh(job)

        _emit(db, job, progress=0)

        media = db.get(MediaFile, job.media_id) if job.media_id else None
        sub = db.get(SubtitleFile, job.subtitle_id) if job.subtitle_id else None

        if not media or not sub:
            job.status = "failed"
            job.error_message = "Missing media or subtitle for sync job."
            job.finished_at = now_utc()
            db.commit()
            db.refresh(job)
            _emit(db, job, progress=100)
            return

        _emit(db, job, progress=30)

        engine_result = run_best_engine(media.path, sub.path)

        _emit(db, job, progress=70, engine_result=engine_result)

        if not engine_result.output_path:
            job.status = "failed"
            job.error_message = engine_result.message or "Engine produced no output."
        else:
            job.status = "completed"
            pairing = db.get(Pairing, job.pairing_id) if job.pairing_id else None
            if pairing:
                pairing.confidence = engine_result.confidence
                pairing.status = "matched"
                db.add(pairing)

        job.finished_at = now_utc()
        db.commit()
        db.refresh(job)

        _emit(db, job, progress=100, engine_result=engine_result)

    except Exception as e:
        try:
            job = db.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.finished_at = now_utc()
                db.commit()
                db.refresh(job)
                _emit(db, job, progress=100)
        finally:
            pass
    finally:
        db.close()
