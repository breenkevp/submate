# app/scanner/scanner.py

from sqlalchemy.orm import Session
from app.scanner.walker import walk_directory
from app.scanner.classifier import classify_file
from app.scanner.ingest import ingest_media, ingest_subtitle
from app.pairing.logic import get_or_create_pairing
from app.workers.queue import enqueue_sync_job
from app.scanner.deletion import mark_deleted_files


def scan(root: str, db: Session):
    media_files = []
    subtitle_files = []

    # First pass: ingest everything
    for path in walk_directory(root):
        file_type = classify_file(path)

        if file_type == "media":
            media = ingest_media(path, db)
            media_files.append(media)

        elif file_type == "subtitle":
            sub = ingest_subtitle(path, db)
            subtitle_files.append(sub)

    # Second pass: create pairings + enqueue jobs
    for media in media_files:
        for sub in subtitle_files:
            pairing = get_or_create_pairing(media.id, sub.id, db)

            if pairing.engine_result_id is None:
                enqueue_sync_job(media.id, sub.id, db)

    # Final pass: mark deleted files
    mark_deleted_files(db)
