import { useRef, useState } from "react";
import Icon from "../components/Icon.jsx";
import { analyzeEmail } from "../api/emailApi.js";

async function isEmlFile(file) {
  if (!file.name.toLowerCase().endsWith(".eml")) return false;
  const text = await file.slice(0, 64 * 1024).text();
  const separator = /\r?\n\r?\n/.test(text);
  const headerLines = text
    .split(/\r?\n/)
    .filter((line) =>
      /^(from|to|cc|bcc|subject|date|message-id|mime-version|content-type|received|return-path):/i.test(
        line,
      ),
    );
  return separator && headerLines.length >= 2;
}

function AnalysisResult({ result }) {
  return (
    <section
      className={`result-card ${result.isPhishing ? "result-phishing" : "result-safe"}`}
      aria-live="polite"
    >
      <div className="result-heading">
        <span className="result-icon">
          {result.isPhishing ? "!" : <Icon name="check" size={22} />}
        </span>
        <div>
          <span className="result-kicker">ANALYSIS COMPLETE</span>
          <h3>
            {result.isPhishing
              ? "This email is likely phishing"
              : "No phishing detected"}
          </h3>
        </div>
      </div>
      {result.summary && <p className="result-summary">{result.summary}</p>}
      {result.isPhishing && result.features.length > 0 && (
        <div className="feature-list">
          <h4>Signals found in this email</h4>
          {result.features.map((feature, index) => (
            <div className="feature-item" key={`${feature.title}-${index}`}>
              <span className="feature-bullet">!</span>
              <div>
                <strong>{feature.title}</strong>
                {feature.description && <p>{feature.description}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
      {result.isPhishing && result.features.length === 0 && (
        <p className="result-summary">
          The analysis flagged this message, but did not return specific
          indicators.
        </p>
      )}
      <p className="result-disclaimer">
        AI results can be imperfect. Avoid clicking links or sharing sensitive
        information if anything seems suspicious.
      </p>
    </section>
  );
}

function StatusNotice({ status, error }) {
  if (status === "invalid") {
    return (
      <div className="notice notice-error" role="alert">
        <span className="notice-symbol">!</span>
        <div>
          <strong>This is not an EML file</strong>
          <p>{error}</p>
        </div>
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="notice notice-error" role="alert">
        <span className="notice-symbol">!</span>
        <div>
          <strong>We couldn’t complete the analysis</strong>
          <p>{error}</p>
        </div>
      </div>
    );
  }
  if (status === "ready") {
    return (
      <div className="notice notice-success" role="status">
        <span className="notice-check">
          <Icon name="check" size={16} />
        </span>
        <div>
          <strong>Valid EML file</strong>
          <p>Your email is ready to be analyzed.</p>
        </div>
      </div>
    );
  }
  if (status === "analyzing") {
    return (
      <div className="progress-panel" role="status" aria-live="polite">
        <span className="spinner" />
        <div>
          <strong>Analyzing your email</strong>
          <p>Checking message content and phishing indicators...</p>
        </div>
        <span className="progress-label">IN PROGRESS</span>
      </div>
    );
  }
  return null;
}

export default function AnalysisPage() {
  const inputRef = useRef(null);
  const fileCheckRef = useRef(0);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function chooseFile(nextFile) {
    setResult(null);
    setError("");
    if (!nextFile) return;
    const checkId = ++fileCheckRef.current;
    setFile(nextFile);
    setStatus("checking");
    if (nextFile.size > 20 * 1024 * 1024) {
      setStatus("invalid");
      setError("This file is larger than the 20 MB limit.");
      return;
    }
    try {
      const valid = await isEmlFile(nextFile);
      if (checkId !== fileCheckRef.current) return;
      setStatus(valid ? "ready" : "invalid");
      setError(
        valid
          ? ""
          : "This is not a valid EML file. Choose an .eml file containing a complete email message.",
      );
    } catch {
      if (checkId !== fileCheckRef.current) return;
      setStatus("invalid");
      setError("The selected file could not be read. Please choose another EML file.");
    }
  }

  async function handleAnalyze() {
    if (!file || !["ready", "error"].includes(status)) return;
    setStatus("analyzing");
    setError("");
    setResult(null);
    try {
      const analysis = await analyzeEmail(file);
      setResult(analysis);
      setStatus("complete");
    } catch (analysisError) {
      setStatus("error");
      setError(analysisError.message);
    }
  }

  function reset() {
    ++fileCheckRef.current;
    setFile(null);
    setStatus("idle");
    setError("");
    setResult(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <main className="page-main analysis-main">
      <section className="page-intro analysis-intro">
        <div className="eyebrow">
          <span className="eyebrow-dot" />
          EMAIL CHECK
        </div>
        <h1>
          Let’s take a <span>closer look.</span>
        </h1>
        <p>
          Upload an .eml file to check for phishing signals. Your result will
          include the indicators that informed the analysis.
        </p>
      </section>

      <section className="analyzer-card" aria-label="Email analyzer">
        <div className="analyzer-card-header">
          <div className="analyzer-step-badge">
            <Icon name="shield" size={19} />
          </div>
          <div>
            <h2>Analyze an email</h2>
            <p>Choose a message file from your device.</p>
          </div>
          <span className="secure-badge">
            <span /> PRIVATE CHECK
          </span>
        </div>
        <div
          className={`drop-zone ${dragging ? "is-dragging" : ""} ${status === "invalid" ? "has-error" : ""}`}
          onDragEnter={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) {
              setDragging(false);
            }
          }}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            chooseFile(event.dataTransfer.files[0]);
          }}
        >
          <input
            ref={inputRef}
            className="visually-hidden"
            type="file"
            accept=".eml,message/rfc822"
            aria-label="Choose an EML file"
            onChange={(event) => chooseFile(event.target.files[0])}
          />
          <div className="upload-illustration">
            <span className="upload-file-icon">
              <Icon name="mail" size={25} />
            </span>
            <span className="upload-arrow-icon">
              <Icon name="upload" size={17} />
            </span>
          </div>
          <h3>{file ? file.name : "Drop your email file here"}</h3>
          <p>
            {file
              ? status === "checking"
                ? "Checking that this is a valid EML message..."
                : `${(file.size / 1024).toFixed(1)} KB · EML file`
              : "or browse files on your device"}
          </p>
          <button
            className="button button-secondary browse-button"
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={status === "analyzing" || status === "checking"}
          >
            {file ? "Choose a different file" : "Browse files"}
          </button>
          <span className="file-note">.EML FORMAT · MAXIMUM SIZE 20 MB</span>
        </div>

        <StatusNotice status={status} error={error} />
        {result && <AnalysisResult result={result} />}

        <div className="analyzer-actions">
          {result ? (
            <button className="button button-secondary" type="button" onClick={reset}>
              Analyze another email
            </button>
          ) : (
            <>
              <button
                className="button button-primary analyze-button"
                type="button"
                onClick={handleAnalyze}
                disabled={!["ready", "error"].includes(status)}
              >
                {status === "analyzing" ? (
                  <>
                    <span className="button-spinner" /> Analyzing...
                  </>
                ) : (
                  <>
                    {status === "error" ? "Try again" : "Analyze email"}{" "}
                    <Icon name="arrow" size={18} />
                  </>
                )}
              </button>
              <a className="text-link" href="#/guides">
                Need help exporting an email?
              </a>
            </>
          )}
        </div>
      </section>
      <p className="privacy-note">
        <Icon name="shield" size={15} />
        Only upload emails you are authorized to share for analysis.
      </p>
    </main>
  );
}
