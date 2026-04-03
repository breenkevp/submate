# app/workers/hash_queue.py

from sqlalchemy.orm import Session
from app.db.models.jobs import Job


def enqueue_hash_job(
    db: Session, media_id: int | None = None, subtitle_id: int | None = None
) -> Job:
    """
    Enqueue a hash job unless one already exists for this file
    that is still queued or running.
    """

    existing = (
        db.query(Job)
        .filter(
            Job.job_type == "hash",
            Job.media_id == media_id,
            Job.subtitle_id == subtitle_id,
            Job.status.in_(["queued", "running"]),
        )
        .first()
    )

    if existing:
        return existing

    job = Job(
        job_type="hash",
        media_id=media_id,
        subtitle_id=subtitle_id,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
