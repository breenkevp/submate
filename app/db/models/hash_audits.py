# app/db/models/hash_audits.py

from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.db.base import Base


class HashAudit(Base):
    __tablename__ = "hash_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # "media" or "subtitle"
    file_type: Mapped[str] = mapped_column(String, nullable=False)

    file_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # What happened?
    event: Mapped[str] = mapped_column(String, nullable=False)

    # Optional details
    old_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    new_hash: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
