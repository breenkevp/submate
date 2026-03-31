from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Pairing(Base):
    __tablename__ = "pairings"

    id = Column(Integer, primary_key=True, index=True)

    media_id = Column(Integer, ForeignKey("media_files.id"), nullable=False)
    subtitle_id = Column(Integer, ForeignKey("subtitle_files.id"), nullable=False)

    # Optional link to engine_results table
    engine_result_id = Column(Integer, ForeignKey("engine_results.id"), nullable=True)

    # Confidence score from the engine (0.0–1.0)
    confidence = Column(Float, nullable=True)

    # Status: "matched", "failed", "manual", etc.
    status = Column(String, nullable=False, default="matched")

    # When this pairing was created
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    media = relationship("MediaFile")
    subtitle = relationship("SubtitleFile")
    engine_result = relationship(
        "EngineResult", back_populates="pairing", uselist=False
    )
