from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .document import DocType, Document


class DocumentStore:
    """In-memory document registry."""

    def __init__(self) -> None:
        self._documents: Dict[str, Document] = {}

    def replace_all(self, documents: Iterable[Document]) -> None:
        """Replace the entire store with a new set of documents."""
        self._documents = {doc.doc_id: doc for doc in documents}

    def add(self, document: Document) -> None:
        self._documents[document.doc_id] = document

    def all(self) -> List[Document]:
        return list(self._documents.values())

    def get(self, doc_id: str) -> Optional[Document]:
        return self._documents.get(doc_id)

    def filter_by_types(self, doc_types: Iterable[DocType]) -> List[Document]:
        doc_type_set = {DocType(dt) if not isinstance(dt, DocType) else dt for dt in doc_types}
        return [doc for doc in self._documents.values() if doc.doc_type in doc_type_set]

    def counts_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for doc in self._documents.values():
            counts[doc.doc_type.value] = counts.get(doc.doc_type.value, 0) + 1
        return counts


