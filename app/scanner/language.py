# app/scanner/language.py

from pathlib import Path
import re

# Common language codes found in subtitle filenames
LANGUAGE_CODES = {
    "en": "English",
    "eng": "English",
    "english": "English",
    "es": "Spanish",
    "spa": "Spanish",
    "spanish": "Spanish",
    "fr": "French",
    "fra": "French",
    "fre": "French",
    "french": "French",
    "de": "German",
    "ger": "German",
    "deu": "German",
    "ita": "Italian",
    "it": "Italian",
    "pt": "Portuguese",
    "por": "Portuguese",
    "ru": "Russian",
    "rus": "Russian",
    "zh": "Chinese",
    "chi": "Chinese",
    "jpn": "Japanese",
    "ja": "Japanese",
    "ko": "Korean",
    "kor": "Korean",
}


def detect_language_from_filename(path: str) -> str | None:
    """
    Detect subtitle language from filename using common patterns.
    Returns a normalized language name or None.
    """
    name = Path(path).stem.lower()

    # Split on dots, dashes, spaces, underscores
    tokens = re.split(r"[.\-_ ]+", name)

    for token in tokens:
        if token in LANGUAGE_CODES:
            return LANGUAGE_CODES[token]

    return None
