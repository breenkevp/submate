from typing import Optional


CONFIDENCE_THRESHOLD = 0.75  # tweak as you learn


class EngineResultData:
    def __init__(
        self,
        engine_name: str,
        confidence: Optional[float],
        message: Optional[str],
        output_path: Optional[str],
        input_media_path: Optional[str] = None,
        input_subtitle_path: Optional[str] = None,
    ):
        self.engine_name = engine_name
        self.confidence = confidence
        self.message = message
        self.output_path = output_path
        self.input_media_path = input_media_path
        self.input_subtitle_path = input_subtitle_path


def run_best_engine(media_path: str, subtitle_path: str) -> EngineResultData:
    # Local import to avoid circular dependancy
    from app.engines.ffsubsync import run_ffsubsync

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
