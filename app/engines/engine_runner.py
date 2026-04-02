from typing import Optional, Tuple


class EngineResultData:
    def __init__(
        self,
        engine_name: str,
        confidence: Optional[float],
        message: Optional[str],
        output_path: Optional[str],
    ):
        self.engine_name = engine_name
        self.confidence = confidence
        self.message = message
        self.output_path = output_path


def run_ffsubsync(media_path: str, subtitle_path: str) -> EngineResultData:
    raise NotImplementedError


def run_autosubsync(media_path: str, subtitle_path: str) -> EngineResultData:
    raise NotImplementedError


def run_best_engine(media_path: str, subtitle_path: str) -> EngineResultData:
    # Try ffsubsync first
    ff = run_ffsubsync(media_path, subtitle_path)

    if ff.output_path and (ff.confidence is None or ff.confidence >= 0.5):
        return ff

    # Fallback to autosubsync
    auto = run_autosubsync(media_path, subtitle_path)

    if auto.output_path:
        return auto

    # Both failed
    return ff if ff.output_path else auto
