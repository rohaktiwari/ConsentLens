import { useMemo } from "react";

type DocType = "email" | "notes" | "cv" | "transcript" | "other";

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

interface ScenarioCardProps {
  scenario: ScenarioResult;
}

const friendlyLabel = (input: string) =>
  input
    .replace(/[_-]/g, " ")
    .split(" ")
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");

const ScenarioCard = ({ scenario }: ScenarioCardProps) => {
  const docTypeLabel = useMemo(
    () => scenario.doc_types.map((type) => friendlyLabel(type)).join(", "),
    [scenario.doc_types],
  );

  return (
    <article className="scenario-card">
      <header>
        <div>
          <h3>{friendlyLabel(scenario.name)}</h3>
          <p className="scenario-meta">
            {scenario.document_count} docs · {docTypeLabel || "All data"}
          </p>
        </div>
      </header>
      {scenario.attributes.length === 0 && <p>No attributes available.</p>}
      {scenario.attributes.map((attribute) => {
        const confidencePercent = Math.round(attribute.confidence * 100);
        return (
          <div key={attribute.name} className="attribute-block">
            <div className="attribute-header">
              <h4>{friendlyLabel(attribute.name)}</h4>
              <span className="confidence-chip">
                {attribute.available ? `${confidencePercent}% confident` : "No signal"}
              </span>
            </div>
            <p className="prediction">
              {attribute.available && attribute.predicted_value
                ? attribute.predicted_value
                : "Not enough evidence in this slice"}
            </p>
            {attribute.top_features.length > 0 && attribute.available && (
              <p className="feature-highlight">
                Signals:{" "}
                <mark>
                  {attribute.top_features
                    .slice(0, 3)
                    .map((feature) => `“${feature}”`)
                    .join(", ")}
                </mark>
              </p>
            )}
            {attribute.supporting_sentences.length > 0 && (
              <div className="supporting-sentences">
                <p>Supporting sentences:</p>
                <ul>
                  {attribute.supporting_sentences.map((sentence) => (
                    <li key={`${sentence.doc_id}-${sentence.text.slice(0, 16)}`}>
                      <strong>{friendlyLabel(sentence.doc_type)}:</strong> {sentence.text}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      })}
    </article>
  );
};

export default ScenarioCard;

