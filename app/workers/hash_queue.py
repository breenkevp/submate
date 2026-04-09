# app/workers/hash_queue.py

from typing import Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.db.models.hash_audits import HashAudit
from app.hashing.hashing import hash_file
from app.events import emit_hash_audit, emit_hash_error
from app.utils.time import now_utc


def enqueue_hash_job(
    db: Session, media_id: int | None = None, subtitle_id: int | None = None
) -> Job:
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


def _record_hash_audit_row(
    db: Session,
    *,
    file_type: str,
    file_id: int,
    event: str,
    old_hash: Optional[str],
    new_hash: Optional[str],
) -> None:
    audit = HashAudit(
        file_type=file_type,
        file_id=file_id,
        event=event,
        old_hash=old_hash,
        new_hash=new_hash,
    )
    db.add(audit)
    db.commit()


def process_media_hash(job_id: int) -> None:
    db: Session = SessionLocal()
    try:
        job: Optional[Job] = db.get(Job, job_id)
        if not job:
            return

        media: Optional[MediaFile] = db.get(MediaFile, job.media_id)
        if not media or not media.path:
            return

        old_hash = media.hash
        try:
            new_hash = hash_file(media.path)
        except Exception as e:
            emit_hash_error(path=media.path, error=str(e))
            return

        status = "unchanged"
        if new_hash is None:
            status = "error"
        elif old_hash != new_hash:
            status = "changed"

        media.hash = new_hash
        db.commit()
        db.refresh(media)

        _record_hash_audit_row(
            db=db,
            file_type="media",
            file_id=media.id,
            event=status,
            old_hash=old_hash,
            new_hash=new_hash,
        )

        emit_hash_audit(
            path=media.path,
            old_hash=old_hash,
            new_hash=new_hash,
            status=status,
        )

        job.status = "completed"
        job.finished_at = now_utc()
        db.commit()

    finally:
        db.close()


def process_subtitle_hash(job_id: int) -> None:
    db: Session = SessionLocal()
    try:
        job: Optional[Job] = db.get(Job, job_id)
        if not job:
            return

        sub: Optional[SubtitleFile] = db.get(SubtitleFile, job.subtitle_id)
        if not sub or not sub.path:
            return

        old_hash = sub.hash
        try:
            new_hash = hash_file(sub.path)
        except Exception as e:
            emit_hash_error(path=sub.path, error=str(e))
            return

        status = "unchanged"
        if new_hash is None:
            status = "error"
        elif old_hash != new_hash:
            status = "changed"

        sub.hash = new_hash
        db.commit()
        db.refresh(sub)

        _record_hash_audit_row(
            db=db,
            file_type="subtitle",
            file_id=sub.id,
            event=status,
            old_hash=old_hash,
            new_hash=new_hash,
        )

        emit_hash_audit(
            path=sub.path,
            old_hash=old_hash,
            new_hash=new_hash,
            status=status,
        )

        job.status = "completed"
        job.finished_at = now_utc()
        db.commit()

    finally:
        db.close()
