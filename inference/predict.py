"""Reusable inference helpers for the classical sentiment model.

Functions
---------
load_artifacts(): returns (vectorizer, model)
predict_sentiment(texts): accepts a string or list[str], returns list[{'label':str,'proba':List[float]}]

CLI demo:
    python -m inference.predict "Some text to classify"

Also shows batch CSV prediction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Union, Tuple

import joblib
import numpy as np

from src.preprocessing.clean_text import batch_clean, clean_text
from train.train_sentiment import LABEL_MAP, INVERSE_LABEL_MAP, MODEL_DIR


def load_artifacts() -> Tuple[any, any]:
    vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.joblib")
    model = joblib.load(MODEL_DIR / "sentiment_logreg.joblib")
    return vectorizer, model


def predict_sentiment(texts: Union[str, List[str]]):
    single_input = False
    if isinstance(texts, str):
        texts = [texts]
        single_input = True

    cleaned = batch_clean(texts)
    vec, clf = load_artifacts()
    X = vec.transform(cleaned)
    probs = clf.predict_proba(X)
    preds = clf.predict(X)

    results = []
    for label_id, prob_vec in zip(preds, probs):
        results.append({
            "label": INVERSE_LABEL_MAP[label_id],
            "confidence_scores": prob_vec.tolist(),
        })

    return results[0] if single_input else results


def _cli():
    parser = argparse.ArgumentParser(description="Classify text sentiment using trained model.")
    parser.add_argument("text", help="Input text or path to CSV with column 'text'")
    parser.add_argument("--output", help="Optional path to save JSON results")
    args = parser.parse_args()

    path = Path(args.text)
    if path.exists():
        import pandas as pd
        df = pd.read_csv(path)
        res = predict_sentiment(df["text"].tolist())
    else:
        res = predict_sentiment(args.text)

    if args.output:
        Path(args.output).write_text(json.dumps(res, indent=2))
    else:
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    _cli()
