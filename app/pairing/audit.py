from sqlalchemy.orm import Session
from app.db.models.pairing_audits import PairingAudit


def record_pairing_audit(
    db: Session,
    pairing_id: int,
    scores: dict,
    decision: str,
):
    audit = PairingAudit(
        pairing_id=pairing_id,
        name_score=scores["name_score"],
        episode_score=scores["episode_score"],
        proximity_score=scores["proximity_score"],
        duration_score=scores["duration_score"],
        language_score=scores["language_score"],
        final_score=scores["final_score"],
        decision=decision,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
