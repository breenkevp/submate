from autosubsync import sync
from pathlib import Path
import tempfile
from .engine_runner import EngineResultData


def run_autosubsync(media_path: str, subtitle_path: str) -> EngineResultData:
    try:
        output_dir = tempfile.mkdtemp(prefix="autosubsync_")
        output_path = str(Path(output_dir) / "synced.srt")

        result = sync(
            reference=media_path,
            target=subtitle_path,
            output=output_path,
        )

        return EngineResultData(
            engine_name="autosubsync",
            confidence=result.confidence if hasattr(result, "confidence") else None,
            message=str(result),
            output_path=output_path if Path(output_path).exists() else None,
        )

    except Exception as e:
        return EngineResultData(
            engine_name="autosubsync",
            confidence=None,
            message=str(e),
            output_path=None,
        )
