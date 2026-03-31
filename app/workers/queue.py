# app/workers/queue.py

from sqlalchemy.orm import Session
from app.db.models.jobs import Job


def enqueue_sync_job(media_id: int, subtitle_id: int, db: Session) -> Job:
    job = Job(
        job_type="sync",
        media_id=media_id,
        subtitle_id=subtitle_id,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
