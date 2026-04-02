import os
import shutil
from time import sleep

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.engine_results import EngineResult
from app.db.models.sync_outputs import SyncOutput
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
        # ATOMIC SUBTITLE REPLACEMENT
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

            # 5. Save SyncOutput record
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
            process_job(job, db)

        db.close()
        sleep(poll_interval)
