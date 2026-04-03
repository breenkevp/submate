from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, Float, ForeignKey
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.media_files import MediaFile


class SubtitleFile(Base):
    __tablename__ = "subtitle_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    path: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    hash: Mapped[str | None] = mapped_column(String, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Incremental scanning fields
    last_scanned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    exists_on_disk: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship back to media
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_files.id"))
    media: Mapped["MediaFile"] = relationship(
        "MediaFile",
        back_populates="subtitles",
    )
