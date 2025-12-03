from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "demo_training_data.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "artifacts"

ATTRIBUTES = [
    "location_region",
    "field_of_study",
    "work_status",
    "income_bracket",
]


def train_attribute(
    attribute: str,
    texts: List[str],
    labels: List[str],
    output_dir: Path,
) -> Path:
    """Train a TF-IDF + LogisticRegression model for one attribute."""

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        min_df=1,
        stop_words="english",
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    classifier = LogisticRegression(max_iter=600, random_state=42, n_jobs=None)
    classifier.fit(tfidf_matrix, labels)

    artifact_path = output_dir / f"{attribute}.joblib"
    joblib.dump(
        {
            "attribute_name": attribute,
            "vectorizer": vectorizer,
            "classifier": classifier,
        },
        artifact_path,
    )
    return artifact_path


def main(data_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(data_path)
    if "text" not in df.columns:
        raise ValueError("Dataset must include a 'text' column.")

    texts = df["text"].fillna("").tolist()
    for attribute in ATTRIBUTES:
        if attribute not in df.columns:
            raise ValueError(f"Dataset missing required column '{attribute}'.")
        labels = df[attribute].fillna("Unknown").tolist()
        artifact_path = train_attribute(attribute, texts, labels, output_dir)
        print(f"✅ Trained {attribute} -> {artifact_path}")  # noqa: T201


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ConsentLens demo models.")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    main(args.data_path, args.output_dir)


