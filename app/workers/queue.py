# app/workers/queue.py

from sqlalchemy.orm import Session
from app.db.models.jobs import Job


def enqueue_sync_job(media_id: int, subtitle_id: int, db: Session) -> Job:
    """
    Enqueue a sync job unless one already exists for this media/subtitle pair
    that is still queued or running.
    """

    # Check for an existing pending job
    existing = (
        db.query(Job)
        .filter(
            Job.media_id == media_id,
            Job.subtitle_id == subtitle_id,
            Job.status.in_(["queued", "running"]),
        )
        .first()
    )

    if existing:
        return existing

    # Otherwise create a new job
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
