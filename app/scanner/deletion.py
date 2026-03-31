# app/scanner/deletion.py

import os
from sqlalchemy.orm import Session
from app.db.models.media_files import MediaFile
from app.db.models.subtitle_files import SubtitleFile


def mark_deleted_files(db: Session):
    """
    Sweep the database and mark any media or subtitle entries
    as missing if the file no longer exists on disk.
    """
    # Media files
    for media in db.query(MediaFile).all():
        if not os.path.exists(media.path):
            media.exists_on_disk = False

    # Subtitle files
    for sub in db.query(SubtitleFile).all():
        if not os.path.exists(sub.path):
            sub.exists_on_disk = False

    db.commit()
