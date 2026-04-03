# app/pairing/hash_audit.py

from app.db.models.hash_audits import HashAudit
from sqlalchemy.orm import Session


def record_hash_audit(
    db: Session,
    file_type: str,
    file_id: int,
    event: str,
    old_hash: str | None = None,
    new_hash: str | None = None,
) -> HashAudit:
    """
    Record a hash/metadata-related audit event for a media or subtitle file.

    file_type: "media" or "subtitle"
    event: short label like "metadata_changed", "hash_created", "unexpected_hash_change"
    """
    audit = HashAudit(
        file_type=file_type,
        file_id=file_id,
        event=event,
        old_hash=old_hash,
        new_hash=new_hash,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
