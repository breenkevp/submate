from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base import Base


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    duration = Column(Float, nullable=True)
    hash = Column(String, nullable=True)

    subtitles = relationship("SubtitleFile", back_populates="media")
