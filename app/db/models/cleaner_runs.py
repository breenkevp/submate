from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class CleanerRun(Base):
    __tablename__ = "cleaner_runs"

    id = Column(Integer, primary_key=True, index=True)

    # Summary of what this run was for (e.g., "daily cleanup", "manual run")
    run_type = Column(String, nullable=False, default="manual")

    # Number of files scanned
    files_scanned = Column(Integer, nullable=False, default=0)

    # Number of files deleted or cleaned
    files_deleted = Column(Integer, nullable=False, default=0)

    # Number of subtitles fixed or renamed
    subtitles_fixed = Column(Integer, nullable=False, default=0)

    # Optional log output from the cleaner
    log_output = Column(Text, nullable=True)

    # Runtime in milliseconds
    runtime_ms = Column(Integer, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
