# app/scanner/scanner.py

from sqlalchemy.orm import Session
from app.scanner.walker import walk_directory
from app.scanner.classifier import classify_file
from app.scanner.ingest import ingest_media, ingest_subtitle
from app.pairing.logic import get_or_create_pairing
from app.workers.queue import enqueue_sync_job
from app.scanner.deletion import mark_deleted_files
from app.pairing.heuristics import score_pairing
from app.pairing.audit import record_pairing_audit

PAIRING_THRESHOLD = 0.5


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
        scored_subs = []

        for sub in subtitle_files:
            scores = score_pairing(media, sub)
            decision = (
                "accepted" if scores["final_score"] >= PAIRING_THRESHOLD else "rejected"
            )

            # Create or fetch pairing
            pairing = get_or_create_pairing(media.id, sub.id, db)

            # Always record audit
            record_pairing_audit(
                db=db,
                pairing_id=pairing.id,
                scores=scores,
                decision=decision,
            )

            scored_subs.append((sub, scores))

        # Pick the best subtitle for this media
        if not scored_subs:
            continue

        best_sub, best_scores = max(
            scored_subs, key=lambda item: item[1]["final_score"]
        )

    # Only enqueue if the best score is acceptable
    if best_scores["final_score"] >= 0.5:
        enqueue_sync_job(media.id, best_sub.id, db)

    # Final pass: mark deleted files
    mark_deleted_files(db)
