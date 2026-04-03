# app/api/media.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.media_files import MediaFile

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_media(db: Session = Depends(get_db)):
    return db.query(MediaFile).all()
