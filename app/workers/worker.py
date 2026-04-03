# app/workers/worker.py

import os
import shutil
from datetime import datetime, timezone
from time import sleep

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.engine_results import EngineResult
from app.db.models.sync_outputs import SyncOutput
from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.db.models.pairings import Pairing
from app.hashing.hashing import hash_file
from app.engines.ffsubsync import run_best_engine
from app.pairing.hash_audit import record_hash_audit


POLL_INTERVAL_SECONDS = 2


def process_sync_job(job: Job, db: Session):
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    db.commit()

    try:
        media: MediaFile | None = job.media
        subtitle: SubtitleFile | None = job.subtitle

        if media is None or subtitle is None:
            job.status = "failed"
            job.error_message = "Sync job missing media or subtitle"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        result = run_best_engine(media.path, subtitle.path)

        # Persist engine result
        engine_result = EngineResult(
            pairing_id=job.pairing_id if job.pairing_id is not None else None,
            engine_name=result.engine_name,
            confidence=result.confidence,
            message=result.message,
        )
        db.add(engine_result)
        db.commit()
        db.refresh(engine_result)

        # If no output_path, treat as failure
        if not result.output_path:
            job.status = "failed"
            job.error_message = (
                "Engine produced no output or below confidence threshold"
            )
            job.engine_result_id = engine_result.id
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        # Move synced subtitle into place (or wherever you want it)
        output_path = result.output_path

        sync_output = SyncOutput(
            output_path=output_path,
            pairing_id=job.pairing_id if job.pairing_id is not None else 0,
            engine_result_id=engine_result.id,
            quality=result.confidence,
            replaced_existing=0,
        )
        db.add(sync_output)

        # Update pairing with engine_result + confidence if present
        if job.pairing_id is not None:
            pairing = db.query(Pairing).get(job.pairing_id)
            if pairing:
                pairing.engine_result_id = engine_result.id
                pairing.confidence = result.confidence
                pairing.status = "matched"

        job.status = "completed"
        job.engine_result_id = engine_result.id
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.finished_at = datetime.now(timezone.utc)
        db.commit()


def process_hash_job(job: Job, db: Session):
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    db.commit()

    try:
        target: MediaFile | SubtitleFile | None = job.media or job.subtitle

        if target is None:
            job.status = "failed"
            job.error_message = "Hash job has no media or subtitle target"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        path = target.path

        if not os.path.exists(path):
            target.exists_on_disk = False
            job.status = "failed"
            job.error_message = f"File missing during hash job: {path}"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        old_hash = target.hash
        new_hash = hash_file(path)

        # First-time hash
        if old_hash is None and new_hash:
            record_hash_audit(
                db=db,
                file_type="media" if job.media_id else "subtitle",
                file_id=target.id,
                event="hash_created",
                new_hash=new_hash,
            )

        # Unexpected change
        if old_hash is not None and new_hash is not None and old_hash != new_hash:
            record_hash_audit(
                db=db,
                file_type="media" if job.media_id else "subtitle",
                file_id=target.id,
                event="unexpected_hash_change",
                old_hash=old_hash,
                new_hash=new_hash,
            )

        target.hash = new_hash

        # Update size + mtime
        stat = os.stat(path)
        target.size = stat.st_size
        target.mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        target.last_scanned_at = datetime.now(timezone.utc)
        target.exists_on_disk = True

        db.add(target)

        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.finished_at = datetime.now(timezone.utc)
        db.commit()


def worker_loop():
    while True:
        db: Session = SessionLocal()
        try:
            job = (
                db.query(Job)
                .filter(Job.status == "queued")
                .order_by(Job.created_at.asc())
                .first()
            )

            if not job:
                db.close()
                sleep(POLL_INTERVAL_SECONDS)
                continue

            if job.job_type == "sync":
                process_sync_job(job, db)
            elif job.job_type == "hash":
                process_hash_job(job, db)
            else:
                job.status = "failed"
                job.error_message = f"Unknown job_type: {job.job_type}"
                job.finished_at = datetime.now(timezone.utc)
                db.commit()

            db.close()

        except Exception:
            db.close()
            sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    worker_loop()
