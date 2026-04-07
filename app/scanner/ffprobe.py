# app/scanner/ffprobe.py

import subprocess
import json
from typing import Optional


def get_duration(path: str) -> Optional[float]:
    """
    Use ffprobe to extract media/subtitle duration in seconds.
    Returns None if ffprobe fails or duration is unavailable.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        data = json.loads(result.stdout)
        duration_str = data.get("format", {}).get("duration")

        if duration_str is None:
            return None

        return float(duration_str)

    except Exception:
        return None
