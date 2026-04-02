from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.pairings import Pairing


class PairingAudit(Base):
    __tablename__ = "pairing_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Link to the pairing this audit entry refers to
    pairing_id: Mapped[int] = mapped_column(ForeignKey("pairings.id"), nullable=False)
    pairing: Mapped["Pairing"] = relationship(
        "Pairing",
        back_populates="audits",
    )

    # Score components
    name_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    episode_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    proximity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    language_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Final weighted score
    final_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Decision: "accepted" or "rejected"
    decision: Mapped[str] = mapped_column(String, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
