from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.media_files import MediaFile
    from app.db.models.subtitle_files import SubtitleFile
    from app.db.models.pairings import Pairing
    from app.db.models.engine_results import EngineResult


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # The type of job: "sync", "scan", "hash", etc.
    job_type: Mapped[str] = mapped_column(String, nullable=False, default="sync")

    # Foreign keys
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_files.id"))
    subtitle_id: Mapped[int | None] = mapped_column(ForeignKey("subtitle_files.id"))
    pairing_id: Mapped[int | None] = mapped_column(ForeignKey("pairings.id"))
    engine_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("engine_results.id")
    )

    # Job status: queued, running, completed, failed, cancelled
    status: Mapped[str] = mapped_column(String, nullable=False, default="queued")

    # Optional error message if failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Worker metadata
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    media: Mapped["MediaFile | None"] = relationship("MediaFile")
    subtitle: Mapped["SubtitleFile | None"] = relationship("SubtitleFile")
    pairing: Mapped["Pairing | None"] = relationship("Pairing")
    engine_result: Mapped["EngineResult | None"] = relationship("EngineResult")
