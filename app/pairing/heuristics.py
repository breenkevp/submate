# app/pairing/heuristics.py

import re
from pathlib import Path
from difflib import SequenceMatcher
from pathlib import Path


def directory_proximity(media_path: str, sub_path: str) -> float:
    """
    Score how close the subtitle is to the media file in the directory tree.
    Returns a score between 0.0 and 1.0.
    """

    media_dir = Path(media_path).parent
    sub_dir = Path(sub_path).parent

    if media_dir == sub_dir:
        return 1.0  # same folder = strongest signal

    # If subtitle is in a subfolder like "Subs" or "Subtitles"
    if sub_dir.parent == media_dir:
        return 0.8

    # If both are in the same season folder
    if media_dir.parent == sub_dir.parent:
        return 0.6

    # If they share a common ancestor folder (e.g., show root)
    if media_dir.parent.parent == sub_dir.parent.parent:
        return 0.4

    # Otherwise weak signal
    return 0.2


def extract_season_episode(name: str):
    """
    Extract SxxEyy pattern from a filename.
    Returns (season, episode) or (None, None).
    """
    match = re.search(r"[Ss](\d{1,2})[Ee](\d{1,2})", name)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def filename_similarity(a: str, b: str) -> float:
    """
    Compute a simple similarity ratio between two filenames.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def language_match(sub_lang: str | None) -> float:
    """
    Score language compatibility.
    For now, we assume media language is unknown.
    """
    if sub_lang is None:
        return 0.5
    return 1.0 if sub_lang.lower() == "english" else 0.3


def score_pairing(media, subtitle) -> float:
    """
    Produce a heuristic score (0.0–1.0) for how likely a subtitle
    belongs to a media file.
    """

    media_name = Path(media.path).stem
    sub_name = Path(subtitle.path).stem

    # 1. Filename similarity
    name_score = filename_similarity(media_name, sub_name)

    # 2. Season/Episode matching
    m_s, m_e = extract_season_episode(media_name)
    s_s, s_e = extract_season_episode(sub_name)

    if m_s is not None and s_s is not None:
        episode_score = 1.0 if (m_s, m_e) == (s_s, s_e) else 0.0
    else:
        episode_score = 0.5

    # 3. Language match
    lang_score = language_match(subtitle.language)

    # 4. Directory proximity
    proximity_score = directory_proximity(media.path, subtitle.path)

    # Weighted score
    return (
        name_score * 0.45
        + episode_score * 0.25
        + proximity_score * 0.20
        + duration_sanity(media.duration, subtitle.duration) * 0.10
        + lang_score * 0.10
    )


def duration_sanity(media_duration: float | None, sub_duration: float | None) -> float:
    """
    Score based on duration similarity.
    Returns 0.0–1.0.
    """
    if media_duration is None or sub_duration is None:
        return 0.5  # neutral

    ratio = min(media_duration, sub_duration) / max(media_duration, sub_duration)

    # If durations are wildly different, penalize heavily
    if ratio < 0.5:
        return 0.0

    return ratio
