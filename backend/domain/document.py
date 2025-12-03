from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DocType(str, Enum):
    """Supported document categories used by downstream analysis."""

    EMAIL = "email"
    CV = "cv"
    NOTES = "notes"
    TRANSCRIPT = "transcript"
    OTHER = "other"


@dataclass
class Document:
    """Normalized representation of a single ingested file."""

    doc_id: str
    source_file: str
    doc_type: DocType
    raw_text: str
    clean_text: str
    description: Optional[str] = None


