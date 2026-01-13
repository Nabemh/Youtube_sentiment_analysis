"""Compute overall satisfaction score for a single YouTube video.

Assumes you already ran the Phase-2 ingestion scripts, producing:
- data/raw/{video_id}_transcript.json  (list[{text,start,duration}])
- data/raw/{video_id}_comments.json    (YouTube commentThreads response)
- data/raw/{video_id}_metadata.json    (snippet + statistics)

Usage
-----
python -m inference.video_sentiment <video_id>

Output (stdout)
----------------
{
  "video_id": "…",
  "score": 78.3,
  "label": "High",
  "components": {
      "transcript_mean": 0.73,
      "comments_mean": 0.81,
      "engagement": 0.65
  }
}
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from .predict import predict_sentiment
MODEL_DIR = Path(__file__).parent.parent / "models"

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"


# -------------------------- helpers ----------------------------------

def _load_transcript(video_id: str) -> List[str]:
    path = RAW_DIR / f"{video_id}_transcript.json"
    if not path.exists():
        return []
    segments = json.loads(path.read_text())
    return [seg["text"] for seg in segments]


def _load_comments(video_id: str) -> List[str]:
    path = RAW_DIR / f"{video_id}_comments.json"
    if not path.exists():
        return []
    threads = json.loads(path.read_text())
    texts: List[str] = []
    for item in threads:
        top = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        texts.append(top)
        for reply in item.get("replies", {}).get("comments", []):
            texts.append(reply["snippet"]["textDisplay"])
    return texts


def _engagement_score(video_id: str) -> float:
    meta_path = RAW_DIR / f"{video_id}_metadata.json"
    if not meta_path.exists():
        return 0.5  # neutral if missing
    stats = json.loads(meta_path.read_text())["statistics"]
    likes = int(stats.get("likeCount", 0))
    views = int(stats.get("viewCount", 1))
    comments = int(stats.get("commentCount", 0))
    engagement = (likes + comments) / views if views else 0.0
    return min(1.0, engagement)  # simple cap


def _sentiment_continuous(results) -> float:
    """Results is list[{'label', 'confidence_scores':[p_neg, p_neu, p_pos]}].
    Map mean probability * index to [0,1]."""
    if not results:
        return 0.5
    probs = np.array([r["confidence_scores"] for r in results])
    mean_prob = probs.mean(axis=0)
    idx = np.array([0, 0.5, 1.0])  # map negative->0, neutral->0.5, positive->1
    return float(np.dot(mean_prob, idx))


def _qualitative(score: float) -> str:
    if score < 0.4:
        return "Low"
    if score < 0.7:
        return "Average"
    return "High"


# ------------------------- main logic --------------------------------

def _model_accuracy() -> float:
    metrics_path = MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        try:
            return json.loads(metrics_path.read_text()).get("accuracy", None)
        except Exception:
            return None
    return None


def analyse_video(video_id: str) -> Dict[str, Any]:
    transcript_texts = _load_transcript(video_id)
    comment_texts = _load_comments(video_id)

    transcript_res = predict_sentiment(transcript_texts) if transcript_texts else []
    comment_res = predict_sentiment(comment_texts) if comment_texts else []

    trans_score = _sentiment_continuous(transcript_res)
    comment_score = _sentiment_continuous(comment_res)
    engage_score = _engagement_score(video_id)

    final = 0.4 * trans_score + 0.4 * comment_score + 0.2 * engage_score
    result = {
        "video_id": video_id,
        "score": round(final * 100, 1),  # percentage
        "label": _qualitative(final),
        "components": {
            "transcript_mean": round(trans_score, 3),
            "comments_mean": round(comment_score, 3),
            "engagement": round(engage_score, 3),
        },
    }
    acc = _model_accuracy()
    result["model_accuracy"] = round(acc * 100, 2) if acc is not None else 0.0
    return result


def _cli():
    parser = argparse.ArgumentParser(description="Compute satisfaction score for a YouTube video")
    parser.add_argument("video_id")
    args = parser.parse_args()
    result = analyse_video(args.video_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
