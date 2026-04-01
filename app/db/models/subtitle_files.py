from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.base import Base


class SubtitleFile(Base):
    __tablename__ = "subtitle_files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    language = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds, if available

    # Incremental scanning fields
    last_scanned_at = Column(DateTime, nullable=True)
    exists_on_disk = Column(Boolean, default=True)

    # Relationship back to media
    media_id = Column(Integer, ForeignKey("media_files.id"))
    media = relationship("MediaFile", back_populates="subtitles")
