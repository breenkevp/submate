# app/scanner/ingest.py

import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.scanner.ffprobe import get_media_duration, get_subtitle_duration
from app.scanner.language import detect_language_from_filename
from app.scanner.change_detection import file_changed
from app.workers.hash_queue import enqueue_hash_job


def ingest_media(path: str, db: Session) -> MediaFile:
    existing = db.query(MediaFile).filter_by(path=path).first()

    if existing:
        # File missing?
        if not os.path.exists(path):
            existing.exists_on_disk = False
            db.commit()
            return existing

        # File changed?
        if file_changed(path, existing):
            enqueue_hash_job(db=db, media_id=existing.id)
            existing.duration = get_media_duration(path)

        existing.last_scanned_at = datetime.now(timezone.utc)
        existing.exists_on_disk = True
        db.commit()
        db.refresh(existing)
        return existing

    # New file
    media = MediaFile(
        path=path,
        hash=None,  # Let hash job fill this in
        duration=get_media_duration(path),
        last_scanned_at=datetime.now(timezone.utc),
        exists_on_disk=True,
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    enqueue_hash_job(db=db, media_id=media.id)

    return media


def ingest_subtitle(path: str, db: Session) -> SubtitleFile:
    existing = db.query(SubtitleFile).filter_by(path=path).first()

    if existing:
        # File missing?
        if not os.path.exists(path):
            existing.exists_on_disk = False
            db.commit()
            return existing

        # File changed?
        if file_changed(path, existing):
            enqueue_hash_job(db=db, subtitle_id=existing.id)
            existing.language = detect_language_from_filename(path)
            existing.duration = get_subtitle_duration(path)

        existing.last_scanned_at = datetime.now(timezone.utc)
        existing.exists_on_disk = True
        db.commit()
        db.refresh(existing)
        return existing

    # New file
    sub = SubtitleFile(
        path=path,
        hash=None,  # Let hash job fill this in
        language=detect_language_from_filename(path),
        duration=get_subtitle_duration(path),
        last_scanned_at=datetime.now(timezone.utc),
        exists_on_disk=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    enqueue_hash_job(db=db, subtitle_id=sub.id)

    return sub
