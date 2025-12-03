from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from typing import Iterable, List

from backend.domain.document import DocType, Document

from .pdf_extraction import extract_text_from_pdf

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def detect_doc_type(file_path: Path) -> DocType:
    """Infer a high-level document type from the filename."""

    name = file_path.name.lower()
    if any(token in name for token in ["mail", "email", "inbox", "sent"]):
        return DocType.EMAIL
    if any(token in name for token in ["cv", "resume"]):
        return DocType.CV
    if any(token in name for token in ["note", "journal"]):
        return DocType.NOTES
    if any(token in name for token in ["transcript", "grade"]):
        return DocType.TRANSCRIPT
    return DocType.OTHER


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)  # strip isolated page numbers
    return text.strip()


def _read_plain_text(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return _read_plain_text(file_path)
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    raise ValueError(f"Unsupported file type: {file_path}")


def ingest_folder(folder_path: Path) -> List[Document]:
    """Walk a folder tree and return normalized Document objects."""

    folder_path = folder_path.expanduser().resolve()
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    documents: List[Document] = []
    for file_path in folder_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.debug("Skipping unsupported file %s", file_path)
            continue
        try:
            raw = _extract_text(file_path)
        except Exception as exc:
            logger.warning("Failed to read %s: %s", file_path, exc)
            continue
        clean = _clean_text(raw)
        doc_type = detect_doc_type(file_path)
        doc = Document(
            doc_id=uuid.uuid4().hex,
            source_file=str(file_path),
            doc_type=doc_type,
            raw_text=raw,
            clean_text=clean,
        )
        documents.append(doc)

    return documents


