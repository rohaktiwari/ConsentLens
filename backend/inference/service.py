from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


@dataclass
class AttributeInference:
    """Explainable prediction for a single attribute."""

    name: str
    predicted_value: Optional[str]
    confidence: float
    top_features: List[str]
    feature_contributions: Dict[str, float]


@dataclass
class AttributeModel:
    """Container for a trained vectorizer + classifier pair."""

    name: str
    vectorizer: TfidfVectorizer
    classifier: LogisticRegression


class InferenceEngine:
    """Loads trained models and performs predictions."""

    def __init__(self, artifacts_dir: Path) -> None:
        self._artifacts_dir = artifacts_dir
        self._models: Dict[str, AttributeModel] = {}
        self._load_models()

    @property
    def is_ready(self) -> bool:
        return bool(self._models)

    def _load_models(self) -> None:
        if not self._artifacts_dir.exists():
            self._artifacts_dir.mkdir(parents=True, exist_ok=True)
            return
        for joblib_file in self._artifacts_dir.glob("*.joblib"):
            payload = joblib.load(joblib_file)
            attribute_name = payload["attribute_name"]
            vectorizer = payload["vectorizer"]
            classifier = payload["classifier"]
            self._models[attribute_name] = AttributeModel(
                name=attribute_name,
                vectorizer=vectorizer,
                classifier=classifier,
            )

    @property
    def attribute_names(self) -> List[str]:
        return sorted(self._models.keys())

    def predict(self, text: str, top_k_features: int = 5) -> Dict[str, AttributeInference]:
        """Generate predictions for every available attribute."""

        if not text.strip() or not self._models:
            return {}
        return {
            name: self._predict_with_model(model, text, top_k_features)
            for name, model in self._models.items()
        }

    def _predict_with_model(
        self,
        model: AttributeModel,
        text: str,
        top_k: int,
    ) -> AttributeInference:
        vector = model.vectorizer.transform([text])
        classifier = model.classifier

        probabilities = classifier.predict_proba(vector)[0]
        best_idx = int(np.argmax(probabilities))
        predicted_value = str(classifier.classes_[best_idx])
        confidence = float(probabilities[best_idx])

        feature_names = model.vectorizer.get_feature_names_out()
        dense_vector = vector.toarray()[0]
        coefs = classifier.coef_[best_idx]
        contributions = dense_vector * coefs

        ranked_indices = np.argsort(contributions)[::-1]
        positive_indices = [idx for idx in ranked_indices if contributions[idx] > 0]

        if not positive_indices:
            tfidf_ranked = np.argsort(dense_vector)[::-1]
            positive_indices = [idx for idx in tfidf_ranked if dense_vector[idx] > 0]
        if not positive_indices:
            positive_indices = ranked_indices[:top_k]

        feature_contributions: Dict[str, float] = {}
        top_features: List[str] = []

        for idx in positive_indices:
            feature = feature_names[idx]
            contribution = float(contributions[idx])
            if feature not in feature_contributions:
                feature_contributions[feature] = contribution
                top_features.append(feature)
            if len(top_features) >= top_k:
                break

        return AttributeInference(
            name=model.name,
            predicted_value=predicted_value,
            confidence=confidence,
            top_features=top_features,
            feature_contributions=feature_contributions,
        )


__all__ = ["AttributeInference", "InferenceEngine"]


