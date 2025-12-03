from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from backend.domain.document import DocType


class FolderIngestRequest(BaseModel):
    """Incoming payload for folder ingestion."""

    folder_path: str = Field(..., description="Absolute path to the folder to ingest.")


class DocumentSummary(BaseModel):
    """Lightweight representation of a stored document."""

    doc_id: str
    doc_type: DocType
    source_file: str
    preview: str


class DocumentDetail(DocumentSummary):
    """Verbose document payload returned by /documents/{doc_id}."""

    raw_text: str
    clean_text: str


class IngestResponse(BaseModel):
    """Response describing the ingestion run."""

    document_count: int
    doc_type_counts: Dict[str, int]
    documents: List[DocumentSummary]


class SupportingSentence(BaseModel):
    """Sentence snippet that backs an attribute prediction."""

    doc_id: str
    doc_type: DocType
    text: str


class AttributeExplanation(BaseModel):
    """Explainable output for a single attribute."""

    name: str
    predicted_value: Optional[str]
    confidence: float
    top_features: List[str]
    supporting_sentences: List[SupportingSentence]
    available: bool = True


class ScenarioResult(BaseModel):
    """Risk scenario summary."""

    name: str
    doc_types: List[DocType]
    document_count: int
    attributes: List[AttributeExplanation]


class AnalysisRequest(BaseModel):
    """Analysis options provided by the UI."""

    doc_types: Optional[List[DocType]] = Field(
        None,
        description=(
            "Optional explicit list of document types to analyze instead of the default"
            " risk scenarios."
        ),
    )
    top_k_features: int = Field(5, ge=1, le=10)
    max_supporting_sentences: int = Field(3, ge=1, le=10)


class AnalysisResponse(BaseModel):
    """Envelope for analyze endpoint."""

    generated_at: datetime
    scenarios: List[ScenarioResult]



