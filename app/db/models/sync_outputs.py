from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.pairings import Pairing
    from app.db.models.engine_results import EngineResult


class SyncOutput(Base):
    __tablename__ = "sync_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Path to the final synced subtitle file
    output_path: Mapped[str] = mapped_column(String, nullable=False)

    # Link to pairing that produced this output
    pairing_id: Mapped[int] = mapped_column(ForeignKey("pairings.id"), nullable=False)
    pairing: Mapped["Pairing"] = relationship("Pairing")

    # Optional link to engine result
    engine_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("engine_results.id"), nullable=True
    )
    engine_result: Mapped["EngineResult | None"] = relationship("EngineResult")

    # Quality score (0.0–1.0)
    quality: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Whether this output replaced an existing subtitle
    replaced_existing: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
