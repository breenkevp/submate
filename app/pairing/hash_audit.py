# app/pairing/hash_audit.py

from sqlalchemy.orm import Session
from app.db.models.hash_audits import HashAudit


def record_hash_audit(
    db: Session,
    file_type: str,
    file_id: int,
    event: str,
    old_hash: str | None = None,
    new_hash: str | None = None,
) -> HashAudit:
    """
    Create a hash/metadata audit entry.
    file_type: "media" or "subtitle"
    event: e.g. "metadata_changed", "hash_created", "unexpected_hash_change"
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
