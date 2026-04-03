# app/scanner/change_detection.py

import os
from datetime import datetime, timezone


def file_changed(path: str, db_obj) -> bool:
    """
    Determine if a file has changed since last scan.
    Uses:
      - file existence
      - stored size
      - stored mtime (timezone-aware)
    """

    # Missing file always counts as changed
    if not os.path.exists(path):
        return True

    stat = os.stat(path)

    # If we have never stored metadata, treat as changed
    if db_obj.mtime is None or db_obj.size is None:
        return True

    # Compute current mtime as timezone-aware
    file_mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)

    # Compare mtime
    if file_mtime != db_obj.mtime:
        return True

    # Compare size
    if stat.st_size != db_obj.size:
        return True

    return False
