from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from backend.domain.document import DocType, Document
from backend.explanation import ExplanationEngine
from backend.inference import InferenceEngine
from backend.schemas import AttributeExplanation, ScenarioResult


@dataclass(frozen=True)
class ScenarioDefinition:
    """Configuration describing which doc types belong to a scenario."""

    name: str
    doc_types: List[DocType]


def run_scenarios(
    documents: Iterable[Document],
    scenarios: List[ScenarioDefinition],
    inference_engine: InferenceEngine,
    explanation_engine: ExplanationEngine,
    top_k_features: int = 5,
    max_supporting_sentences: int = 3,
) -> List[ScenarioResult]:
    """Execute all requested scenarios and collect explainable predictions."""

    documents_list = list(documents)
    return [
        _run_single_scenario(
            documents_list,
            scenario,
            inference_engine,
            explanation_engine,
            top_k_features,
            max_supporting_sentences,
        )
        for scenario in scenarios
    ]


def _run_single_scenario(
    documents: List[Document],
    scenario: ScenarioDefinition,
    inference_engine: InferenceEngine,
    explanation_engine: ExplanationEngine,
    top_k_features: int,
    max_supporting_sentences: int,
) -> ScenarioResult:
    doc_type_filter = set(scenario.doc_types)
    scenario_docs = [doc for doc in documents if doc.doc_type in doc_type_filter]
    combined_text = "\n\n".join(doc.clean_text for doc in scenario_docs).strip()

    predictions = (
        inference_engine.predict(combined_text, top_k_features=top_k_features)
        if combined_text
        else {}
    )

    attributes: List[AttributeExplanation] = []

    if not scenario_docs:
        attributes = [
            AttributeExplanation(
                name=name,
                predicted_value=None,
                confidence=0.0,
                top_features=[],
                supporting_sentences=[],
                available=False,
            )
            for name in inference_engine.attribute_names
        ]
    else:
        for name in inference_engine.attribute_names:
            inference = predictions.get(name)
            if not inference:
                attributes.append(
                    AttributeExplanation(
                        name=name,
                        predicted_value=None,
                        confidence=0.0,
                        top_features=[],
                        supporting_sentences=[],
                        available=False,
                    )
                )
                continue
            supporting_sentences = explanation_engine.collect_supporting_sentences(
                scenario_docs,
                inference.top_features,
                limit=max_supporting_sentences,
            )
            attributes.append(
                AttributeExplanation(
                    name=name,
                    predicted_value=inference.predicted_value,
                    confidence=inference.confidence,
                    top_features=inference.top_features,
                    supporting_sentences=supporting_sentences,
                    available=True,
                )
            )

    return ScenarioResult(
        name=scenario.name,
        doc_types=scenario.doc_types,
        document_count=len(scenario_docs),
        attributes=attributes,
    )



