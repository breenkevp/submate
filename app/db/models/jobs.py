from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    # The type of job: "sync", "scan", "hash", etc.
    job_type = Column(String, nullable=False, default="sync")

    # Foreign keys
    media_id = Column(Integer, ForeignKey("media_files.id"), nullable=True)
    subtitle_id = Column(Integer, ForeignKey("subtitle_files.id"), nullable=True)
    pairing_id = Column(Integer, ForeignKey("pairings.id"), nullable=True)
    engine_result_id = Column(Integer, ForeignKey("engine_results.id"), nullable=True)

    # Job status: queued, running, completed, failed, cancelled
    status = Column(String, nullable=False, default="queued")

    # Optional error message if failed
    error_message = Column(Text, nullable=True)

    # Worker metadata
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Relationships
    media = relationship("MediaFile")
    subtitle = relationship("SubtitleFile")
    pairing = relationship("Pairing")
    engine_result = relationship("EngineResult")
