"""Fetch top-level comments and replies for a YouTube video.

Usage:
    python -m ingest.fetch_comments <video_id> [max_comments]
Saves to data/raw/{video_id}_comments.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from googleapiclient.errors import HttpError

from .youtube_client import get_service

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
DEFAULT_DIR.mkdir(parents=True, exist_ok=True)


def get_comments(video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """Return up to `max_results` comments (top-level + replies)."""
    service = get_service()
    comments: List[Dict[str, Any]] = []
    page_token = None

    while len(comments) < max_results:
        try:
            resp = (
                service.commentThreads()
                .list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=page_token,
                    textFormat="plainText",
                )
                .execute()
            )
        except HttpError as e:
            raise RuntimeError(f"YouTube API error while fetching comments: {e}") from e

        for item in resp.get("items", []):
            comments.append(item)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return comments


def save_comments(video_id: str, comments, out_path: Path | None = None):
    if out_path is None:
        out_path = DEFAULT_DIR / f"{video_id}_comments.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(comments)} comments to {out_path}")


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: fetch_comments <video_id> [max_comments]")

    video_id = sys.argv[1]
    max_comments = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    comments = get_comments(video_id, max_comments)
    save_comments(video_id, comments)


if __name__ == "__main__":
    main()
