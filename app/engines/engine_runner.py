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
