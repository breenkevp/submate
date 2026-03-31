# app/scanner/walker.py

import os
from typing import Iterator, List


DEFAULT_IGNORE_DIRS = {".git", "__pycache__", ".DS_Store"}


def walk_directory(root: str, ignore_dirs: List[str] | None = None) -> Iterator[str]:
    """
    Recursively walk a directory and yield file paths.

    Args:
        root: The root directory to scan.
        ignore_dirs: Optional list of directory names to ignore.

    Yields:
        Full file paths.
    """
    if ignore_dirs is None:
        ignore_dirs = []

    ignore_set = DEFAULT_IGNORE_DIRS.union(ignore_dirs)

    for dirpath, dirnames, filenames in os.walk(root):
        # Remove ignored directories from traversal
        dirnames[:] = [d for d in dirnames if d not in ignore_set]

        for filename in filenames:
            yield os.path.join(dirpath, filename)
