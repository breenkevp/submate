# app/api/pairings.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.pairings import Pairing

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_pairings(db: Session = Depends(get_db)):
    return db.query(Pairing).all()
