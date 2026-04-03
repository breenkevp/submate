from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.pairings import Pairing


class EngineResult(Base):
    __tablename__ = "engine_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Link back to pairing
    pairing_id: Mapped[int] = mapped_column(
        ForeignKey("pairings.id"),
        nullable=False,
    )
    pairing: Mapped["Pairing"] = relationship(
        "Pairing",
        back_populates="engine_result",
    )

    # Engine metadata
    engine_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )  # e.g., "ffsubsync"

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    message: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
