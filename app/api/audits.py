# app/api/audits.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.hash_audits import HashAudit

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/hash")
def list_hash_audits(db: Session = Depends(get_db)):
    return db.query(HashAudit).order_by(HashAudit.created_at.desc()).limit(200).all()
