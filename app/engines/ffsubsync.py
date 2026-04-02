import subprocess
import tempfile
from pathlib import Path
from .engine_runner import EngineResultData


def run_ffsubsync(media_path: str, subtitle_path: str) -> EngineResultData:
    try:
        output_dir = tempfile.mkdtemp(prefix="ffsubsync_")
        output_path = str(Path(output_dir) / "synced.srt")

        cmd = [
            "ffsubsync",
            media_path,
            "-i",
            subtitle_path,
            "-o",
            output_path,
            "--overwrite",
            "--verbose",
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        # ffsubsync prints confidence like: "Sync accuracy: 0.87"
        confidence = None
        for line in result.stdout.splitlines():
            if "accuracy" in line.lower():
                try:
                    confidence = float(line.split()[-1])
                except:
                    pass

        return EngineResultData(
            engine_name="ffsubsync",
            confidence=confidence,
            message=result.stdout + "\n" + result.stderr,
            output_path=output_path if Path(output_path).exists() else None,
        )

    except Exception as e:
        return EngineResultData(
            engine_name="ffsubsync",
            confidence=None,
            message=str(e),
            output_path=None,
        )
