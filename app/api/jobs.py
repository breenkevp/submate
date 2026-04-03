# app/api/jobs.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.jobs import Job

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).limit(200).all()
