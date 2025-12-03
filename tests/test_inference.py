from pathlib import Path

from backend.inference import InferenceEngine
from backend.models.train_models import DEFAULT_DATASET, main as train_main


def test_inference_returns_predictions(tmp_path):
    artifacts_dir = Path(tmp_path) / "artifacts"
    train_main(DEFAULT_DATASET, artifacts_dir)

    engine = InferenceEngine(artifacts_dir)
    assert engine.is_ready

    sample_text = (
        "I take the MBTA to Cambridge for my MIT computer science lab and polish "
        "case studies for a consulting club."
    )
    predictions = engine.predict(sample_text, top_k_features=3)

    assert "location_region" in predictions
    location_pred = predictions["location_region"]
    assert location_pred.predicted_value is not None
    assert 0 <= location_pred.confidence <= 1
    assert len(location_pred.top_features) <= 3

