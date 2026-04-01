from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Text
from app.db.base import Base


class CleanerRun(Base):
    __tablename__ = "cleaner_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Summary of what this run was for (e.g., "daily cleanup", "manual run")
    run_type: Mapped[str] = mapped_column(String, nullable=False, default="manual")

    # Number of files scanned
    files_scanned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Number of files deleted or cleaned
    files_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Number of subtitles fixed or renamed
    subtitles_fixed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Optional log output from the cleaner
    log_output: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Runtime in milliseconds
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
