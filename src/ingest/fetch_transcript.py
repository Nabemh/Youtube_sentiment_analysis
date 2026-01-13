"""Download transcript for a single YouTube video and save to JSON.

Usage:
    python -m ingest.fetch_transcript <video_id> [output_path]
Saves default to data/raw/{video_id}_transcript.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)


def get_transcript(video_id: str) -> List[Dict[str, Any]]:
    """Return transcript segments as list of dicts with text, start, duration."""
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=("en",))
        return fetched.to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise RuntimeError(f"No transcript available for {video_id}: {e}") from e


def save_transcript(video_id: str, segments, out_path: Path | None = None):
    if out_path is None:
        out_path = DEFAULT_DIR / f"{video_id}_transcript.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"Saved transcript to {out_path}")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: fetch_transcript <video_id> [output_path]")

    video_id = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    segments = get_transcript(video_id)
    save_transcript(video_id, segments, out)


if __name__ == "__main__":
    main()
