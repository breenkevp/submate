from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.media_files import MediaFile
    from app.db.models.subtitle_files import SubtitleFile
    from app.db.models.engine_results import EngineResult
    from app.db.models.pairing_audits import PairingAudit


class Pairing(Base):
    __tablename__ = "pairings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    audits: Mapped[list["PairingAudit"]] = relationship(
        "PairingAudit",
        back_populates="pairing",
        cascade="all, delete-orphan",
    )

    media_id: Mapped[int] = mapped_column(
        ForeignKey("media_files.id"),
        nullable=False,
    )
    subtitle_id: Mapped[int] = mapped_column(
        ForeignKey("subtitle_files.id"),
        nullable=False,
    )

    # Optional link to engine_results table
    engine_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("engine_results.id"),
        nullable=True,
    )

    # Confidence score from the engine (0.0–1.0)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Status: "matched", "failed", "manual", etc.
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="matched",
    )

    # When this pairing was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    media: Mapped["MediaFile"] = relationship("MediaFile")
    subtitle: Mapped["SubtitleFile"] = relationship("SubtitleFile")
    engine_result: Mapped["EngineResult | None"] = relationship(
        "EngineResult",
        back_populates="pairing",
        uselist=False,
    )
