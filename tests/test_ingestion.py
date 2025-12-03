from pathlib import Path

from backend.domain.document import DocType
from backend.ingestion.file_ingestion import ingest_folder


def test_ingest_folder_reads_supported_files(tmp_path):
    sample_dir = Path(tmp_path)
    email_file = sample_dir / "my_email.txt"
    notes_file = sample_dir / "project_notes.md"
    unsupported = sample_dir / "image.jpg"

    email_file.write_text("From: test@example.com\nSubject: Hello Boston", encoding="utf-8")
    notes_file.write_text("Daily journal entry about research progress.", encoding="utf-8")
    unsupported.write_text("binary", encoding="utf-8")

    documents = ingest_folder(sample_dir)

    assert len(documents) == 2
    doc_types = {doc.doc_type for doc in documents}
    assert DocType.EMAIL in doc_types
    assert DocType.NOTES in doc_types

