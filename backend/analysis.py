"""Backend utility wrapping the sentiment pipeline for a single video.
Exports one function `analyse_video(video_id: str)` that returns the same JSON
structure produced previously by the CLI script.

Relies on directories:
- backend/../../data/raw  (transcripts, comments, metadata)
- backend/../../models    (saved model + metrics)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# locate project root = two levels up from this file
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
MODEL_DIR = ROOT / "models"

from importlib import import_module

# lazy-load predict_sentiment from inference.predict inside backend move.
try:
    predict_sentiment = import_module("inference.predict").predict_sentiment
except ModuleNotFoundError:
    # when files moved inside backend, adjust path
    from sys import path as _sp

    _sp.append(str(ROOT))
    predict_sentiment = import_module("inference.predict").predict_sentiment  # type: ignore


def _load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _load_texts(video_id: str) -> tuple[List[str], List[str]]:
    trans_path = RAW_DIR / f"{video_id}_transcript.json"
    comm_path = RAW_DIR / f"{video_id}_comments.json"
    transcript_texts = []
    comment_texts = []

    segs = _load_json(trans_path)
    if segs:
        transcript_texts = [s["text"] for s in segs]

    threads = _load_json(comm_path)
    if threads:
        for item in threads:
            comment_texts.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )
            for reply in item.get("replies", {}).get("comments", []):
                comment_texts.append(reply["snippet"]["textDisplay"])
    return transcript_texts, comment_texts


def _sentiment_continuous(result_list):
    if not result_list:
        return 0.5
    probs = np.array([r["confidence_scores"] for r in result_list])
    mean_prob = probs.mean(axis=0)
    idx = np.array([0, 0.5, 1.0])
    return float(np.dot(mean_prob, idx))


def _engagement(video_id: str) -> float:
    meta_path = RAW_DIR / f"{video_id}_metadata.json"
    data = _load_json(meta_path)
    if not data:
        return 0.0
    stats = data["statistics"]
    likes = int(stats.get("likeCount", 0))
    views = int(stats.get("viewCount", 1))
    comments = int(stats.get("commentCount", 0))
    return min(1.0, (likes + comments) / views) if views else 0.0


def _qualitative(score: float) -> str:
    if score < 0.4:
        return "Low"
    if score < 0.7:
        return "Average"
    return "High"


def _model_accuracy() -> float | None:
    met = _load_json(MODEL_DIR / "metrics.json")
    return float(met["accuracy"]) if met else None


def analyse_video(video_id: str) -> Dict[str, Any]:
    transcript, comments = _load_texts(video_id)
    trans_res = predict_sentiment(transcript) if transcript else []
    comm_res = predict_sentiment(comments) if comments else []

    t_score = _sentiment_continuous(trans_res)
    c_score = _sentiment_continuous(comm_res)
    e_score = _engagement(video_id)

    final = 0.4 * t_score + 0.4 * c_score + 0.2 * e_score
    resp = {
        "video_id": video_id,
        "score": round(final * 100, 1),
        "label": _qualitative(final),
        "components": {
            "transcript_mean": round(t_score, 3),
            "comments_mean": round(c_score, 3),
            "engagement": round(e_score, 3),
        },
    }
    acc = _model_accuracy()
    if acc is not None:
        resp["model_accuracy"] = round(acc * 100, 2)
    return resp
