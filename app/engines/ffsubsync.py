import subprocess
import tempfile
from pathlib import Path
from .engine_runner import EngineResultData, CONFIDENCE_THRESHOLD


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
            input_media_path=media_path,
            input_subtitle_path=subtitle_path,
        )

    except Exception as e:
        return EngineResultData(
            engine_name="ffsubsync",
            confidence=None,
            message=str(e),
            output_path=None,
            input_media_path=media_path,
            input_subtitle_path=subtitle_path,
        )


def run_best_engine(media_path: str, subtitle_path: str) -> EngineResultData:

    result = run_ffsubsync(media_path, subtitle_path)

    # If ffsubsync produced no file, it's a hard failure
    if not result.output_path:
        return result

    # If confidence is missing, treat as low-confidence but usable
    if result.confidence is None:
        return result

    # Enforce threshold
    if result.confidence >= CONFIDENCE_THRESHOLD:
        return result

    # Below threshold: treat as failure by clearing output_path
    result.message = (
        (result.message or "")
        + f"\n[engine] confidence {result.confidence:.2f} below threshold {CONFIDENCE_THRESHOLD:.2f}"
    )
    result.output_path = None
    return result
