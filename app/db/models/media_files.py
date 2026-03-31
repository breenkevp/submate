from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

last_scanned_at = Column(DateTime, nullable=True)
exists_on_disk = Column(Boolean, default=True)


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    duration = Column(Float, nullable=True)
    hash = Column(String, nullable=True)

    subtitles = relationship("SubtitleFile", back_populates="media")
