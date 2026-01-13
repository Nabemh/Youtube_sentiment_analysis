"""Fetch basic video metadata (likes, views, publish date).

Usage:
    python -m ingest.fetch_metadata <video_id>
Saves to data/raw/{video_id}_metadata.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from .youtube_client import get_video_metadata

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)



def save_metadata(video_id: str, meta: Dict[str, Any], out_path: Path | None = None):
    if out_path is None:
        out_path = DEFAULT_DIR / f"{video_id}_metadata.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Saved metadata to {out_path}")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: fetch_metadata <video_id>")
    video_id = sys.argv[1]
    meta = get_video_metadata(video_id)
    save_metadata(video_id, meta)


if __name__ == "__main__":
    main()
