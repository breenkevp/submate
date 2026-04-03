# app/api/scan.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.scanner.scanner import scan

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def trigger_scan(root: str, db: Session = Depends(get_db)):
    scan(root, db)
    return {"status": "scan_started", "root": root}
