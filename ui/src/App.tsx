import { FormEvent, useState } from "react";
import ScenarioCard from "./components/ScenarioCard";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type DocType = "email" | "notes" | "cv" | "transcript" | "other";

interface DocumentSummary {
  doc_id: string;
  doc_type: DocType;
  source_file: string;
  preview: string;
}

interface SupportSentence {
  doc_id: string;
  doc_type: DocType;
  text: string;
}

interface AttributeExplanation {
  name: string;
  predicted_value: string | null;
  confidence: number;
  top_features: string[];
  supporting_sentences: SupportSentence[];
  available: boolean;
}

interface ScenarioResult {
  name: string;
  doc_types: DocType[];
  document_count: number;
  attributes: AttributeExplanation[];
}

interface IngestResponse {
  document_count: number;
  doc_type_counts: Record<string, number>;
  documents: DocumentSummary[];
}

interface AnalysisResponse {
  generated_at: string;
  scenarios: ScenarioResult[];
}

function App() {
  const [folderPath, setFolderPath] = useState("");
  const [loadingIngest, setLoadingIngest] = useState(false);
  const [ingestSummary, setIngestSummary] = useState<IngestResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleIngest = async (event: FormEvent) => {
    event.preventDefault();
    setErrorMessage(null);
    setAnalysis(null);
    setLoadingIngest(true);
    try {
      const response = await fetch(`${API_BASE_URL}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder_path: folderPath }),
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail ?? "Ingestion failed");
      }
      const data = (await response.json()) as IngestResponse;
      setIngestSummary(data);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Unknown error during ingestion.");
      }
    } finally {
      setLoadingIngest(false);
    }
  };

  const handleAnalyze = async () => {
    if (!ingestSummary) {
      setErrorMessage("Ingest some files first.");
      return;
    }
    setLoadingAnalysis(true);
    setErrorMessage(null);
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail ?? "Analysis failed");
      }
      const data = (await response.json()) as AnalysisResponse;
      setAnalysis(data);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Unknown error during analysis.");
      }
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const renderDocTypeCounts = () => {
    if (!ingestSummary) {
      return null;
    }
    return Object.entries(ingestSummary.doc_type_counts).map(([docType, count]) => (
      <div key={docType} className="doc-type-pill">
        <span>{docType}</span>
        <strong>{count}</strong>
      </div>
    ));
  };

  return (
    <div className="app-shell">
      <header>
        <div>
          <h1>ConsentLens</h1>
          <p className="subtitle">Local, explainable privacy risk analysis for your documents.</p>
        </div>
        <div className="status-chip">
          API: <span className="status-dot" />
          {API_BASE_URL}
        </div>
      </header>

      <section className="card">
        <h2>1. Select a folder</h2>
        <form className="ingest-form" onSubmit={handleIngest}>
          <input
            type="text"
            placeholder="C:\\Users\\you\\Documents\\my-data"
            value={folderPath}
            onChange={(event) => setFolderPath(event.target.value)}
            required
          />
          <button type="submit" disabled={loadingIngest}>
            {loadingIngest ? "Ingesting…" : "Ingest Folder"}
          </button>
        </form>
        <p className="helper-text">
          Your files never leave this machine. ConsentLens reads .txt, .md, and .pdf files recursively.
        </p>
        {errorMessage && <p className="error">{errorMessage}</p>}
      </section>

      {ingestSummary && (
        <section className="card">
          <h2>2. Ingestion summary</h2>
          <p>
            {ingestSummary.document_count} documents processed. Breakdown by heuristic document type:
          </p>
          <div className="doc-type-grid">{renderDocTypeCounts()}</div>
          <details>
            <summary>Show ingested files</summary>
            <ul className="document-list">
              {ingestSummary.documents.map((doc) => (
                <li key={doc.doc_id}>
                  <strong>{doc.doc_type}</strong>
                  <span>{doc.source_file}</span>
                  <p>{doc.preview}</p>
                </li>
              ))}
            </ul>
          </details>
          <button className="primary" onClick={handleAnalyze} disabled={loadingAnalysis}>
            {loadingAnalysis ? "Analyzing…" : "Run Privacy Risk Analysis"}
          </button>
        </section>
      )}

      {analysis && (
        <section className="card">
          <h2>3. Risk scenarios</h2>
          <p>
            Generated at {new Date(analysis.generated_at).toLocaleString()}. Compare what different
            document slices reveal.
          </p>
          <div className="scenario-grid">
            {analysis.scenarios.map((scenario) => (
              <ScenarioCard key={scenario.name} scenario={scenario} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;

