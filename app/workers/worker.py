# app/workers/worker.py

import os
import asyncio
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
from app.websockets.manager import manager


POLL_INTERVAL_SECONDS = 2


def process_sync_job(job: Job, db: Session):
    from app.websockets.events import broadcast_event  # local import avoids circulars

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

            broadcast_event(
                "sync_job_update",
                {
                    "job_id": job.id,
                    "status": job.status,
                    "error_message": job.error_message,
                },
            )
            return

        # Run engine
        result = run_best_engine(media.path, subtitle.path)

        # Persist engine result
        engine_result = EngineResult(
            pairing_id=job.pairing_id,
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

            broadcast_event(
                "sync_job_update",
                {
                    "job_id": job.id,
                    "status": job.status,
                    "engine_result_id": engine_result.id,
                    "error_message": job.error_message,
                },
            )
            return

        # Save sync output
        sync_output = SyncOutput(
            output_path=result.output_path,
            pairing_id=job.pairing_id if job.pairing_id else 0,
            engine_result_id=engine_result.id,
            quality=result.confidence,
            replaced_existing=0,
        )
        db.add(sync_output)

        # Update pairing if present
        if job.pairing_id:
            pairing = db.query(Pairing).get(job.pairing_id)
            if pairing:
                pairing.engine_result_id = engine_result.id
                pairing.confidence = result.confidence
                pairing.status = "matched"

        # Finalize job
        job.status = "completed"
        job.engine_result_id = engine_result.id
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

        broadcast_event(
            "sync_job_update",
            {
                "job_id": job.id,
                "status": job.status,
                "media_id": job.media_id,
                "subtitle_id": job.subtitle_id,
                "pairing_id": job.pairing_id,
                "engine_result_id": job.engine_result_id,
                "confidence": result.confidence,
                "output_path": result.output_path,
            },
        )

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

        broadcast_event(
            "sync_job_update",
            {
                "job_id": job.id,
                "status": job.status,
                "error_message": job.error_message,
            },
        )


def process_hash_job(job: Job, db: Session):
    from app.websockets.events import broadcast_event  # local import avoids circulars

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

            broadcast_event(
                "hash_job_update",
                {
                    "job_id": job.id,
                    "status": job.status,
                    "error_message": job.error_message,
                },
            )
            return

        path = target.path

        if not os.path.exists(path):
            target.exists_on_disk = False
            job.status = "failed"
            job.error_message = f"File missing during hash job: {path}"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()

            broadcast_event(
                "hash_job_update",
                {
                    "job_id": job.id,
                    "status": job.status,
                    "error_message": job.error_message,
                },
            )
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

        # Hash changed
        elif old_hash and new_hash and old_hash != new_hash:
            record_hash_audit(
                db=db,
                file_type="media" if job.media_id else "subtitle",
                file_id=target.id,
                event="unexpected_hash_change",
                old_hash=old_hash,
                new_hash=new_hash,
            )

            # Invalidate pairings
            if job.media_id:
                for p in db.query(Pairing).filter_by(media_id=target.id).all():
                    p.status = "stale"
            else:
                for p in db.query(Pairing).filter_by(subtitle_id=target.id).all():
                    p.status = "stale"

        # Update hash + metadata
        target.hash = new_hash

        stat = os.stat(path)
        target.size = stat.st_size
        target.mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        target.last_scanned_at = datetime.now(timezone.utc)
        target.exists_on_disk = True

        db.add(target)

        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

        broadcast_event(
            "hash_job_update",
            {
                "job_id": job.id,
                "status": job.status,
                "media_id": job.media_id,
                "subtitle_id": job.subtitle_id,
                "pairing_id": job.pairing_id,
                "old_hash": old_hash,
                "new_hash": new_hash,
            },
        )

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

        broadcast_event(
            "hash_job_update",
            {
                "job_id": job.id,
                "status": job.status,
                "error_message": job.error_message,
            },
        )


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
