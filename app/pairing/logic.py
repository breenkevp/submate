# app/pairing/logic.py

from sqlalchemy.orm import Session
from app.db.models.pairings import Pairing


def get_or_create_pairing(media_id: int, subtitle_id: int, db: Session) -> Pairing:
    existing = (
        db.query(Pairing).filter_by(media_id=media_id, subtitle_id=subtitle_id).first()
    )
    if existing:
        return existing

    pairing = Pairing(media_id=media_id, subtitle_id=subtitle_id, status="pending")
    db.add(pairing)
    db.commit()
    db.refresh(pairing)
    return pairing
