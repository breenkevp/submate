import os
import shutil
from datetime import datetime
from time import sleep

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.engine_results import EngineResult
from app.db.models.sync_outputs import SyncOutput
from app.hashing.hashing import hash_file
from app.engines.ffsubsync import run_best_engine


def process_job(job: Job, db: Session):
    """Run a single sync job."""
    job.status = "running"
    db.commit()

    media = job.media
    subtitle = job.subtitle

    # These should always exist for sync jobs
    assert media is not None
    assert subtitle is not None

    try:
        # Run engine pipeline (ffsubsync only)
        result = run_best_engine(media.path, subtitle.path)

        # Save engine result
        engine_result = EngineResult(
            pairing_id=job.pairing_id,
            engine_name=result.engine_name,
            confidence=result.confidence,
            message=result.message,
        )
        db.add(engine_result)
        db.commit()
        db.refresh(engine_result)

        job.engine_result_id = engine_result.id

        # Update Pairing
        pairing = job.pairing
        if pairing:
            pairing.engine_result_id = engine_result.id
            pairing.confidence = result.confidence

            if result.output_path:
                pairing.status = "matched"
            else:
                pairing.status = "failed"

        # ------------------------------------------------------------------
        # SAFE ATOMIC SUBTITLE REPLACEMENT
        # ------------------------------------------------------------------
        if result.output_path:
            assert result.input_subtitle_path is not None
            assert result.output_path is not None

            original_path = result.input_subtitle_path
            new_path = result.output_path
            backup_path = original_path + ".bak"

            replaced_existing = 0

            try:
                # 1. Backup original subtitle (if it exists)
                if os.path.exists(original_path):
                    shutil.copy2(original_path, backup_path)
                    replaced_existing = 1

                # 2. Atomically replace original with synced subtitle
                os.replace(new_path, original_path)

                # 3. Replacement succeeded — remove backup
                if os.path.exists(backup_path):
                    os.remove(backup_path)

            except Exception as replace_error:
                # 4. Restore backup if replacement failed
                if os.path.exists(backup_path):
                    os.replace(backup_path, original_path)

                job.status = "failed"
                job.error_message = f"Subtitle replacement failed: {replace_error}"
                db.commit()
                return

            # ------------------------------------------------------------------
            # UPDATE SUBTITLE HASH + METADATA
            # ------------------------------------------------------------------
            try:
                subtitle.hash = hash_file(original_path)
                subtitle.last_scanned_at = datetime.utcnow()
                subtitle.exists_on_disk = True
                db.add(subtitle)
            except Exception as hash_error:
                job.status = "failed"
                job.error_message = f"Hash update failed: {hash_error}"
                db.commit()
                return

            # ------------------------------------------------------------------
            # CLEAN UP FFSUBSYNC TEMP DIRECTORY
            # ------------------------------------------------------------------
            try:
                temp_dir = os.path.dirname(new_path)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                # Non-fatal — temp cleanup failure shouldn't break the job
                pass

            # ------------------------------------------------------------------
            # SAVE SyncOutput RECORD
            # ------------------------------------------------------------------
            sync_output = SyncOutput(
                pairing_id=job.pairing_id,
                engine_result_id=engine_result.id,
                output_path=original_path,
                quality=result.confidence or 0.0,
                replaced_existing=replaced_existing,
            )
            db.add(sync_output)
            job.status = "completed"

        else:
            job.status = "failed"
            job.error_message = result.message

        # Final durable commit
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()


def worker_loop(poll_interval: int = 3):
    """Continuously process queued jobs."""
    while True:
        db = SessionLocal()

        job = (
            db.query(Job)
            .filter(Job.status == "queued")
            .order_by(Job.created_at.asc())
            .first()
        )

        if job:
            if job.job_type == "hash":
                process_hash_job(job, db)
            else:
                process_job(job, db)

        db.close()
        sleep(poll_interval)


def process_hash_job(job: Job, db: Session):
    """Compute and update the hash for a media or subtitle file."""
    job.status = "running"
    db.commit()

    try:
        # Determine which file this job refers to
        target = job.media or job.subtitle

        if target is None:
            job.status = "failed"
            job.error_message = "Hash job has no media or subtitle target"
            db.commit()
            return

        path = target.path

        # File missing?
        if not os.path.exists(path):
            target.exists_on_disk = False
            job.status = "failed"
            job.error_message = f"File missing during hash job: {path}"
            db.commit()
            return

        # Compute hash
        new_hash = hash_file(path)

        # Update DB fields
        target.hash = new_hash
        target.last_scanned_at = datetime.utcnow()
        target.exists_on_disk = True

        # Optional future fields:
        # target.size = os.path.getsize(path)
        # target.mtime = datetime.fromtimestamp(os.path.getmtime(path))

        db.add(target)

        job.status = "completed"
        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
