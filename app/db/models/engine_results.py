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


class EngineResult(Base):
    __tablename__ = "engine_results"

    id = Column(Integer, primary_key=True, index=True)

    # Link back to pairing
    pairing_id = Column(Integer, ForeignKey("pairings.id"), nullable=False)
    pairing = relationship("Pairing", back_populates="engine_result")

    # Engine metadata
    engine_name = Column(String, nullable=False)  # e.g., "ffsubsync"
    confidence = Column(Float, nullable=True)
    message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
