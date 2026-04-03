# app/scanner/change_detection.py

import os
from datetime import datetime, timezone


def file_changed(path: str, db_obj) -> bool:
    """
    Determine if a file has changed since last scan.
    Compares:
      - file existence
      - mtime (timezone-aware)
      - file size
    """

    # Missing file always counts as changed
    if not os.path.exists(path):
        return True

    stat = os.stat(path)

    # If never scanned, treat as changed
    if db_obj.last_scanned_at is None:
        return True

    # Compare mtime (db_obj.mtime is timezone-aware)
    file_mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc)

    if db_obj.mtime is None:
        # No stored mtime → treat as changed
        return True

    if file_mtime != db_obj.mtime:
        return True

    # Compare size
    if db_obj.size is None or db_obj.size != stat.st_size:
        return True

    return False
