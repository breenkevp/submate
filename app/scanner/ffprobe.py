# app/scanner/ffprobe.py

import subprocess
import json


def get_media_duration(path: str) -> float | None:
    """
    Use ffprobe to extract media duration in seconds.
    Returns None if ffprobe fails.
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
