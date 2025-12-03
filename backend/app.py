from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.analysis import ScenarioDefinition, run_scenarios
from backend.domain.document import DocType, Document
from backend.domain.store import DocumentStore
from backend.explanation import ExplanationEngine
from backend.ingestion.file_ingestion import ingest_folder
from backend.inference import InferenceEngine
from backend.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    DocumentDetail,
    DocumentSummary,
    FolderIngestRequest,
    IngestResponse,
)


BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "models" / "artifacts"

DEFAULT_SCENARIOS = [
    ScenarioDefinition(name="emails_only", doc_types=[DocType.EMAIL]),
    ScenarioDefinition(name="notes_only", doc_types=[DocType.NOTES]),
    ScenarioDefinition(name="cv_only", doc_types=[DocType.CV]),
    ScenarioDefinition(
        name="all_data",
        doc_types=[DocType.EMAIL, DocType.NOTES, DocType.CV, DocType.TRANSCRIPT, DocType.OTHER],
    ),
]

app = FastAPI(title="ConsentLens API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_store = DocumentStore()
inference_engine = InferenceEngine(ARTIFACT_DIR)
explanation_engine = ExplanationEngine()


def _summarize_documents(documents: List[Document], preview_length: int = 320) -> List[DocumentSummary]:
    summaries: List[DocumentSummary] = []
    for doc in documents:
        preview = doc.clean_text[:preview_length] + ("…" if len(doc.clean_text) > preview_length else "")
        summaries.append(
            DocumentSummary(
                doc_id=doc.doc_id,
                doc_type=doc.doc_type,
                source_file=doc.source_file,
                preview=preview,
            )
        )
    return summaries


@app.get("/health")
def healthcheck() -> dict:
    """Simple readiness probe."""

    return {
        "status": "ok",
        "documents_indexed": len(document_store.all()),
        "models_loaded": inference_engine.is_ready,
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: FolderIngestRequest) -> IngestResponse:
    """Recursively ingest the requested folder."""

    documents = ingest_folder(Path(request.folder_path))
    if not documents:
        raise HTTPException(status_code=400, detail="No supported documents were found in that folder.")
    document_store.replace_all(documents)
    return IngestResponse(
        document_count=len(documents),
        doc_type_counts=document_store.counts_by_type(),
        documents=_summarize_documents(documents),
    )


@app.get("/documents", response_model=List[DocumentSummary])
def list_documents() -> List[DocumentSummary]:
    """Return a lightweight catalog of all ingested documents."""

    return _summarize_documents(document_store.all())


@app.get("/documents/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: str) -> DocumentDetail:
    """Return the raw + clean text for a single document."""

    document = document_store.get(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    preview = document.clean_text[:320] + ("…" if len(document.clean_text) > 320 else "")
    return DocumentDetail(
        doc_id=document.doc_id,
        doc_type=document.doc_type,
        source_file=document.source_file,
        preview=preview,
        raw_text=document.raw_text,
        clean_text=document.clean_text,
    )


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Run attribute inference for the requested document sets."""

    documents = document_store.all()
    if not documents:
        raise HTTPException(status_code=400, detail="Ingest documents before running analysis.")
    if not inference_engine.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Models are not available yet. Run backend/models/train_models.py first.",
        )

    if request.doc_types:
        try:
            doc_types = [DocType(dt) if not isinstance(dt, DocType) else dt for dt in request.doc_types]
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid document type in request.") from exc
        scenarios = [ScenarioDefinition(name="custom_selection", doc_types=doc_types)]
    else:
        scenarios = DEFAULT_SCENARIOS

    scenario_results = run_scenarios(
        documents=documents,
        scenarios=scenarios,
        inference_engine=inference_engine,
        explanation_engine=explanation_engine,
        top_k_features=request.top_k_features,
        max_supporting_sentences=request.max_supporting_sentences,
    )

    return AnalysisResponse(generated_at=datetime.utcnow(), scenarios=scenario_results)



