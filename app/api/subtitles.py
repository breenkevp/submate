# app/api/subtitles.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.subtitle_files import SubtitleFile

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_subtitles(db: Session = Depends(get_db)):
    return db.query(SubtitleFile).all()
