# app/scanner/ingest.py

# app/scanner/ingest.py

import os
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile
from app.hashing.hashing import hash_file
from app.scanner.ffprobe import get_media_duration
from app.scanner.language import detect_language_from_filename
from app.scanner.change_detection import file_changed


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
            new_hash = hash_file(path)

            if existing.hash != new_hash:
                # Replacement detected
                existing.hash = new_hash
                existing.duration = get_media_duration(path)

        existing.last_scanned_at = datetime.utcnow()
        existing.exists_on_disk = True
        db.commit()
        db.refresh(existing)
        return existing

    # New file
    media = MediaFile(
        path=path,
        hash=hash_file(path),
        duration=get_media_duration(path),
        last_scanned_at=datetime.utcnow(),
        exists_on_disk=True,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
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
            new_hash = hash_file(path)

            if existing.hash != new_hash:
                # Replacement detected
                existing.hash = new_hash
                existing.language = detect_language_from_filename(path)

        existing.last_scanned_at = datetime.utcnow()
        existing.exists_on_disk = True
        db.commit()
        db.refresh(existing)
        return existing

    # New file
    sub = SubtitleFile(
        path=path,
        hash=hash_file(path),
        language=detect_language_from_filename(path),
        last_scanned_at=datetime.utcnow(),
        exists_on_disk=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub
