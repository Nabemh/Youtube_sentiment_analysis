"""YouTube Data API helper.
Loads API key from environment and returns an authenticated service object.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def _get_api_key() -> str:
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise EnvironmentError(
            "YOUTUBE_API_KEY not set. Add it to your .env file or environment vars."
        )
    return key


@lru_cache(maxsize=1)
def get_service():
    """Return a cached YouTube Data API service client."""
    api_key = _get_api_key()
    return build(API_SERVICE_NAME, API_VERSION, developerKey=api_key)


def get_video_metadata(video_id: str) -> Dict[str, Any]:
    """Return snippet and statistics for a single YouTube video id."""
    service = get_service()
    try:
        response = (
            service.videos()
            .list(part="snippet,statistics,contentDetails", id=video_id)
            .execute()
        )
    except HttpError as e:
        raise RuntimeError(f"YouTube API error: {e}") from e

    items = response.get("items", [])
    if not items:
        raise ValueError(f"No video found for id {video_id}")
    return items[0]
