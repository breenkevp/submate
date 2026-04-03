# app/hashing/hashing.py

import hashlib
import os
from typing import Optional


HASH_CHUNK_SIZE = 1024 * 1024  # 1 MB chunks (tunable)


def hash_file(path: str) -> Optional[str]:
    """
    Compute a SHA-256 hash of a file in streaming mode.
    Returns the hex digest string, or None if the file is missing or unreadable.
    """

    if not os.path.exists(path):
        return None

    try:
        sha = hashlib.sha256()

        with open(path, "rb") as f:
            while True:
                chunk = f.read(HASH_CHUNK_SIZE)
                if not chunk:
                    break
                sha.update(chunk)

        return sha.hexdigest()

    except Exception:
        # File unreadable, permission denied, etc.
        return None
