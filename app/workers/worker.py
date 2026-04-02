from time import sleep
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.jobs import Job
from app.db.models.engine_results import EngineResult
from app.db.models.sync_outputs import SyncOutput
from app.engines.engine_runner import run_best_engine


def process_job(job: Job, db: Session):
    """Run a single sync job."""
    job.status = "running"
    db.commit()

    media = job.media
    subtitle = job.subtitle

    try:
        # Run engine pipeline (ffsubsync → autosubsync fallback)
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

        # Save sync output if successful
        if result.output_path:
            sync_output = SyncOutput(
                pairing_id=job.pairing_id,
                engine_result_id=engine_result.id,
                output_path=result.output_path,
                quality=result.confidence or 0.0,
                replaced_existing=0,
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
