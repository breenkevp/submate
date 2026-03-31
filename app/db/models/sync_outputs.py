from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class SyncOutput(Base):
    __tablename__ = "sync_outputs"

    id = Column(Integer, primary_key=True, index=True)

    # Path to the final synced subtitle file
    output_path = Column(String, nullable=False)

    # Link to pairing that produced this output
    pairing_id = Column(Integer, ForeignKey("pairings.id"), nullable=False)
    pairing = relationship("Pairing")

    # Optional link to engine result
    engine_result_id = Column(Integer, ForeignKey("engine_results.id"), nullable=True)
    engine_result = relationship("EngineResult")

    # Quality score (0.0–1.0)
    quality = Column(Float, nullable=True)

    # Whether this output replaced an existing subtitle
    replaced_existing = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
