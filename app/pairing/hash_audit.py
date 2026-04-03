# app/pairing/hash_audit.py

from app.db.models.hash_audits import HashAudit


def record_hash_audit(db, file_type, file_id, event, old_hash=None, new_hash=None):
    audit = HashAudit(
        file_type=file_type,
        file_id=file_id,
        event=event,
        old_hash=old_hash,
        new_hash=new_hash,
    )
    db.add(audit)
    db.commit()
    return audit
