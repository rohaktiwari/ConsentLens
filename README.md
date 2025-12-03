# ConsentLens

Local, explainable privacy risk analyzer for the files that live on your machine. ConsentLens ingests plaintext, markdown, and PDF documents; runs transparent TF-IDF + logistic regression models; and surfaces human-readable explanations so you can understand what an attacker could infer from different slices of your digital exhaust.

## Highlights
- Local-only processing – the backend never makes network calls.
- Simple heuristics categorize files into `email`, `notes`, `cv`, `transcript`, or `other`.
- Attribute models (location region, field of study, work status, income bracket) are trained with scikit-learn and persisted as `joblib` artifacts.
- Explanation layer remaps top TF-IDF features back to actual sentences for justification.
- Risk simulation compares attacker views: emails only, notes only, CV only, and all data.
- Minimal React + Vite UI for ingestion, summaries, and side-by-side scenario cards.

## Repository Layout
```
backend/        FastAPI app, ingestion pipeline, explainability + inference
backend/models  Training script and pre-trained artifacts
backend/analysis Scenario orchestration for attacker slices
backend/ingestion File + PDF readers and cleaners
backend/explanation Feature → sentence mapper (spaCy sentencizer)
backend/schemas  Pydantic request/response contracts
data/           Demo CSV used to train sample models
tests/          Pytest suites for ingestion and inference
ui/             React (Vite) frontend
requirements.txt Python dependencies
```

## Prerequisites
- Python 3.10+
- Node.js 18+ (for the UI)
- (Recommended) A virtual environment for Python dependencies

## Backend Setup
```bash
# from the repo root
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
```

### Train or Refresh Demo Models
Pre-trained artifacts live under `backend/models/artifacts/`. Re-train them any time using the bundled synthetic dataset:
```bash
python backend/models/train_models.py
# or specify custom data / output paths:
# python backend/models/train_models.py --data-path data/demo_training_data.csv --output-dir backend/models/artifacts
```

### Run the API
```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```
Key endpoints (auto-documented at `/docs`):
- `GET /health` – readiness probe.
- `POST /ingest` – body `{ "folder_path": "/path/to/files" }`; returns counts + previews.
- `GET /documents` – list of stored docs.
- `GET /documents/{doc_id}` – raw + clean text for one doc.
- `POST /analyze` – optional `doc_types` filter; returns scenario-level predictions with supporting sentences.

## UI Setup
```bash
cd ui
npm install
npm run dev
```
The UI expects the API at `http://localhost:8000` by default. Override by defining `VITE_API_BASE_URL` in a `.env` file or your shell before `npm run dev`.

## End-to-End Flow
1. Start the FastAPI backend (`uvicorn …`).
2. Launch the Vite dev server (`npm run dev`), then open the printed URL (typically `http://localhost:5173`).
3. Enter a folder path containing `.txt`, `.md`, or `.pdf` files and ingest.
4. Review ingestion counts and document previews.
5. Click **Run Privacy Risk Analysis** to compare attacker scenarios:
   - Only emails
   - Only notes
   - Only CVs
   - All data
6. Each scenario lists attribute predictions, confidence, and the sentences that contributed to the inference.

## Running Tests
```bash
pytest
```
`test_ingestion.py` verifies recursive file handling and doc-type detection. `test_inference.py` retrains the toy models in a temp directory and ensures predictions include confidences and top features.

## Assumptions & Notes
- File classification relies on filename keywords (`cv`, `resume`, `note`, etc.). Adjust `detect_doc_type` for finer-grained rules.
- SpaCy’s lightweight English pipeline with a sentencizer is used to avoid large model downloads.
- All computation is in-memory; there is no persistence layer yet.
- Models are illustrative only—they are trained on a small synthetic dataset to demonstrate end-to-end behavior.


