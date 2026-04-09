# app/scanner/ingest.py

import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.db.models.pairings import Pairing
from app.scanner.ffprobe import get_duration
from app.scanner.language import detect_language_from_filename
from app.scanner.change_detection import file_changed
from app.workers.hash_queue import enqueue_hash_job
from app.pairing.hash_audit import record_hash_audit


def ingest_media(path: str, db: Session) -> MediaFile:
    existing = db.query(MediaFile).filter_by(path=path).first()

    if existing:
        if not os.path.exists(path):
            existing.exists_on_disk = False
            db.commit()
            return existing

        if file_changed(path, existing):
            record_hash_audit(
                db=db,
                file_type="media",
                file_id=existing.id,
                event="metadata_changed",
            )

            for p in db.query(Pairing).filter_by(media_id=existing.id).all():
                p.status = "stale"

            enqueue_hash_job(db=db, media_id=existing.id)
            existing.duration = get_duration(path)

            stat = os.stat(path)
            existing.size = stat.st_size
            existing.mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)

        existing.last_scanned_at = datetime.now(timezone.utc)
        existing.exists_on_disk = True
        db.commit()
        db.refresh(existing)
        return existing

    stat = os.stat(path)

    media = MediaFile(
        path=path,
        hash=None,
        duration=get_duration(path),
        last_scanned_at=datetime.now(timezone.utc),
        exists_on_disk=True,
        size=stat.st_size,
        mtime=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    enqueue_hash_job(db=db, media_id=media.id)

    return media


def ingest_subtitle(path: str, db: Session) -> SubtitleFile:
    existing = db.query(SubtitleFile).filter_by(path=path).first()

    if existing:
        if not os.path.exists(path):
            existing.exists_on_disk = False
            db.commit()
            return existing

        if file_changed(path, existing):
            record_hash_audit(
                db=db,
                file_type="subtitle",
                file_id=existing.id,
                event="metadata_changed",
            )

            for p in db.query(Pairing).filter_by(subtitle_id=existing.id).all():
                p.status = "stale"

            enqueue_hash_job(db=db, subtitle_id=existing.id)
            existing.language = detect_language_from_filename(path)
            existing.duration = get_duration(path)

            stat = os.stat(path)
            existing.size = stat.st_size
            existing.mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)

        existing.last_scanned_at = datetime.now(timezone.utc)
        existing.exists_on_disk = True
        db.commit()
        db.refresh(existing)
        return existing

    stat = os.stat(path)

    sub = SubtitleFile(
        path=path,
        hash=None,
        language=detect_language_from_filename(path),
        duration=get_duration(path),
        last_scanned_at=datetime.now(timezone.utc),
        exists_on_disk=True,
        size=stat.st_size,
        mtime=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    enqueue_hash_job(db=db, subtitle_id=sub.id)

    return sub
