# app/scanner/change_detection.py

import os
from datetime import datetime


def file_changed(path: str, db_obj) -> bool:
    """
    Determine if a file has changed since last scan.
    Compares:
      - file existence
      - mtime
      - file size
    """
    if not os.path.exists(path):
        return True  # treat missing as changed

    stat = os.stat(path)

    # If never scanned, treat as changed
    if db_obj.last_scanned_at is None:
        return True

    # If mtime is newer than last scan, treat as changed
    if datetime.fromtimestamp(stat.st_mtime) > db_obj.last_scanned_at:
        return True

    # Extra safety: if size changed, treat as changed
    if hasattr(db_obj, "size") and db_obj.size is not None:
        if stat.st_size != db_obj.size:
            return True

    return False
