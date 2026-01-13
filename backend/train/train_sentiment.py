"""Train a classical (scikit-learn) sentiment classifier.

Steps implemented (matches project requirements):
1. Data validation & merge of all CSVs in data/
2. Label normalization → int {0,1,2}
3. Lightweight text preprocessing (clean_text)
4. TF-IDF vectorization (unigrams+bigrams, 10k features)
5. Stratified 80/20 split
6. LogisticRegression training (liblinear)
7. Evaluation: accuracy, precision/recall/F1, confusion matrix
8. Error analysis: print 10 hardest examples per class
9. Model persistence via joblib (model + vectorizer) to models/

Run:
    python -m train.train_sentiment --data_dir data

Outputs saved in models/ and metrics printed to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from ..src.preprocessing.clean_text import batch_clean

LABEL_MAP = {"negative": 0, "neutral": 1, "positive": 2}
INVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}
MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset(csv_dir: Path) -> pd.DataFrame:
    files: List[Path] = list(csv_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")

    frames = []
    for f in files:
        df = pd.read_csv(f)
        if not {"text", "label"}.issubset(df.columns):
            # silently skip helper CSVs like video_ids.csv
            continue
        frames.append(df[["text", "label"]])
    if not frames:
        raise ValueError("No valid dataset CSVs with text and label columns found.")
    data = pd.concat(frames, ignore_index=True)
    return data


def validate_dataset(df: pd.DataFrame):
    print("=== DATASET VALIDATION ===")
    total = len(df)
    print(f"Total samples: {total}")
    invalid_rows = df[ df["text"].isna() | df["label"].isna() ]
    print(f"Missing rows: {len(invalid_rows)}")
    # Drop invalid
    df.dropna(subset=["text", "label"], inplace=True)
    # Strip whitespace
    df["label"] = df["label"].str.lower().str.strip()
    dist = df["label"].value_counts()
    print("Class distribution:\n", dist.to_dict())


def normalize_labels(df: pd.DataFrame):
    before = len(df)
    df["label_id"] = df["label"].map(LABEL_MAP)
    df.dropna(subset=["label_id"], inplace=True)
    after = len(df)
    if before != after:
        raise ValueError("Some labels were lost during normalization – check label names!")


def preprocess_texts(texts: List[str]) -> List[str]:
    return batch_clean(texts)


def train(df: pd.DataFrame):
    X_clean = preprocess_texts(df["text"].tolist())
    y = df["label_id"].values

    # Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10000,
        lowercase=False,  # already lowered
    )
    X = vectorizer.fit_transform(X_clean)

    # Split
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X,
        y,
        df.index,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Model
    clf = LogisticRegression(max_iter=1000, n_jobs=-1, solver="lbfgs")
    clf.fit(X_train, y_train)

    # Eval
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test,
        y_pred,
        target_names=[INVERSE_LABEL_MAP[i] for i in range(3)],
        output_dict=True,
    )

    print(f"\nOverall accuracy: {acc:.3f}")
    print("\nClassification report:")
    from pprint import pprint

    pprint(report)
    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save metrics
    metrics_path = MODEL_DIR / "metrics.json"
    metrics_path.write_text(
        json.dumps({"accuracy": acc, "report": report}, indent=2)
    )
    print(f"Saved metrics to {metrics_path}")

    # Error analysis – simple: print a few misclassified examples
    errors = (
        pd.DataFrame({
            "text": df.loc[idx_test, "text"],
            "true": y_test,
            "pred": y_pred,
        })
        .query("true != pred")
    )
    print("\nSample misclassifications:")
    for _, row in errors.sample(min(10, len(errors))).iterrows():
        print(f"TRUE={INVERSE_LABEL_MAP[row.true]} | PRED={INVERSE_LABEL_MAP[row.pred]} | {row.text[:120]}…")

    # Persist
    joblib.dump(clf, MODEL_DIR / "sentiment_logreg.joblib")
    joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.joblib")
    print(f"\nSaved model + vectorizer to {MODEL_DIR}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data", help="Directory with CSV files")
    args = parser.parse_args()

    df = load_dataset(Path(args.data_dir))
    validate_dataset(df)
    normalize_labels(df)
    train(df)


if __name__ == "__main__":
    main()
