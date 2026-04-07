# app/workers/path_utils.py

import os


def normalize_path(path: str) -> str:
    """
    Normalize a host path into the container-visible media root.

    Uses:
      MEDIA_SHARE: host-side root (e.g. /mnt/media4tb/data)
      MEDIA_ROOT:  container-side root (e.g. /media)

    Falls back to /mnt/media -> /media if unset.
    """
    if not path:
        return path

    host_root = os.getenv("MEDIA_SHARE", "/mnt/media")
    container_root = os.getenv("MEDIA_ROOT", "/media")

    if not host_root.endswith("/"):
        host_root += "/"
    if not container_root.endswith("/"):
        container_root += "/"

    if path.startswith(host_root):
        return container_root + path[len(host_root) :]

    return path
