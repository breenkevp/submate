from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Boolean, DateTime, Integer
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.subtitle_files import SubtitleFile


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    path: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    hash: Mapped[str | None] = mapped_column(String, nullable=True)

    # Incremental scanning fields
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exists_on_disk: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    subtitles: Mapped[list["SubtitleFile"]] = relationship(
        "SubtitleFile",
        back_populates="media",
    )
