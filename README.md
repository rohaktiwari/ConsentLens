ConsentLens

ConsentLens is a local, explainable privacy risk analysis system that explores what personal attributes can be inferred from everyday personal documents under different attacker visibility assumptions. The project prioritizes transparency, auditability, and interpretability over predictive performance, with the goal of making privacy leakage inspectable rather than opaque.

Rather than treating inference as a black box, ConsentLens surfaces human-readable justifications—mapping model features back to concrete sentences—so users can understand why specific attributes are inferred and under what data exposure scenarios.

Motivation

Modern ML systems can infer sensitive personal attributes from seemingly innocuous text. However, most privacy analyses focus on aggregate risk or abstract metrics, offering little insight into what information is being used or how partial data exposure changes inference behavior.

ConsentLens investigates a simple question:

Given different slices of a person’s local data (e.g., emails only vs. CV only), what attributes can be inferred, and what evidence supports those inferences?

System Overview

ConsentLens operates entirely locally and consists of three main stages:

Ingestion
Plaintext, Markdown, and PDF documents are ingested and lightly cleaned. Simple heuristics categorize files into coarse types (email, notes, CV, transcript, other).

Inference
Attribute classifiers (TF-IDF + logistic regression) predict coarse attributes such as region, field of study, work status, or income bracket. Models are intentionally simple to preserve interpretability.

Explanation & Risk Simulation
Feature importances are mapped back to the sentences that contributed most strongly to each prediction. The system compares multiple attacker views (e.g., emails only, notes only, all documents) to highlight how inference risk changes with visibility.

Design Rationale

Several design choices were made deliberately:

Linear models over deep models
TF-IDF + logistic regression were chosen to favor interpretability and stability over raw accuracy.

Local-only execution
All computation happens on-device to avoid introducing new privacy risks during analysis.

Explicit attacker modeling
Inference is evaluated under partial data exposure scenarios rather than assuming full access.

Sentence-level explanations
Explanations are grounded in actual text spans to make inferences debuggable by humans.

Repository Structure
backend/        FastAPI backend, ingestion + inference pipeline
backend/models  Training scripts and persisted model artifacts
backend/analysis Attacker scenario orchestration
backend/ingestion File and PDF readers
backend/explanation Feature-to-sentence mapping
backend/schemas  Pydantic request/response models
ui/             React (Vite) frontend
data/           Synthetic demo training data
tests/          Pytest suites for ingestion and inference

Usage (Local)

Backend

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload


Frontend

cd ui
npm install
npm run dev


The UI connects to the backend at http://localhost:8000 by default.

Limitations

Models are trained on a small synthetic dataset and are not intended for real-world deployment.

Document type detection relies on filename heuristics.

The system does not currently model adversarial manipulation of input text.

No persistence layer is implemented; all analysis is in-memory.

Possible Extensions

Studying how explanation fidelity degrades under document obfuscation or redaction.

Comparing linear explanations with attention- or gradient-based attribution methods.

Evaluating user trust when explanations are incomplete or conflicting.

Extending attacker models to include temporal or cross-document correlations.

Notes

This project is intended as an exploratory research system rather than a production privacy tool. The emphasis is on understanding what is inferred and why, not on maximizing predictive accuracy.
