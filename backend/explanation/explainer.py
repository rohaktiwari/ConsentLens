from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, List

import spacy

from backend.domain.document import Document
from backend.schemas import SupportingSentence


class ExplanationEngine:
    """Maps model features back to human-friendly supporting sentences."""

    def __init__(self, cache_size: int = 256) -> None:
        self._nlp = spacy.blank("en")
        if "sentencizer" not in self._nlp.pipe_names:
            self._nlp.add_pipe("sentencizer")
        self._sentence_cache: OrderedDict[str, List[str]] = OrderedDict()
        self._cache_size = cache_size

    def _cache_sentences(self, key: str, sentences: List[str]) -> None:
        self._sentence_cache[key] = sentences
        self._sentence_cache.move_to_end(key)
        if len(self._sentence_cache) > self._cache_size:
            self._sentence_cache.popitem(last=False)

    def sentences_for_document(self, doc_id: str, text: str) -> List[str]:
        """Return cached sentences for a document, computing them on demand."""

        if doc_id in self._sentence_cache:
            self._sentence_cache.move_to_end(doc_id)
            return self._sentence_cache[doc_id]
        doc = self._nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        self._cache_sentences(doc_id, sentences)
        return sentences

    def collect_supporting_sentences(
        self,
        documents: Iterable[Document],
        feature_terms: Iterable[str],
        limit: int = 3,
    ) -> List[SupportingSentence]:
        """Return the first `limit` sentences that contain any of the feature terms."""

        normalized_terms = [term.lower() for term in feature_terms if term]
        if not normalized_terms:
            return []

        hits: List[SupportingSentence] = []
        seen_keys = set()

        for doc in documents:
            sentences = self.sentences_for_document(doc.doc_id, doc.raw_text)
            for sentence in sentences:
                sentence_key = (doc.doc_id, sentence)
                if sentence_key in seen_keys:
                    continue
                lower_sentence = sentence.lower()
                if any(term in lower_sentence for term in normalized_terms):
                    hits.append(
                        SupportingSentence(doc_id=doc.doc_id, doc_type=doc.doc_type, text=sentence)
                    )
                    seen_keys.add(sentence_key)
                    if len(hits) >= limit:
                        return hits
        return hits


__all__ = ["ExplanationEngine"]


