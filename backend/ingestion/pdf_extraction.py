from __future__ import annotations

from pathlib import Path
from typing import Optional

from pdfminer.high_level import extract_text as pdfminer_extract_text
from pypdf import PdfReader


def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF file using pdfminer with a pypdf fallback."""

    try:
        text = pdfminer_extract_text(str(path))
        if text:
            return text
    except Exception:
        # Fall back to pypdf if pdfminer fails on the document.
        pass

    try:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as exc:  # pragma: no cover - exercised via integration
        raise ValueError(f"Unable to extract text from PDF: {path}") from exc


