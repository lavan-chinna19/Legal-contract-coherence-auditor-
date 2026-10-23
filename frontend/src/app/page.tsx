"use client";

import React, { useState, useEffect, useRef } from "react";
import { ReleaseTools } from "../components/ReleaseTools";
import { AppShell } from "../components/layout/AppShell";
import { NavSection } from "../components/layout/SidebarNav";
import { ThemeProvider } from "../components/layout/ThemeContext";
import { EmptyState } from "../components/ui/EmptyState";
import { ContractReviewWorkspace } from "../components/review/ContractReviewWorkspace";
import { AnalyticsWorkspace } from "../components/analytics";
import { ExplainabilityWorkspace } from "../components/explainability";
import { RedTeamWorkspace } from "../components/redteam";
import { DocumentResult } from "../components/review/types";
import { BookOpenCheck, MessageSquareCheck, ArrowRight } from "lucide-react";

interface ParsedContract {
  doc_id: string;
  source_text: string;
  clauses: { clause_id: string; sequence_idx: number; text: string; char_start: number; char_end: number }[];
}

export default function AuditorDashboard() {
  const [backendUrl, setBackendUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
  );
  const [apiKey, setApiKey] = useState(
    ""
  );
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");

  // Navigation State (Primary views + Robustness Lab + Transparency)
  const [activeSection, setActiveSection] = useState<NavSection>("overview");
  const [activeTab, setActiveTab] = useState<"upload" | "results" | "xai" | "feedback" | "redteam" | "transparency">("upload");

  // Privacy acknowledgment
  const [privacyAcknowledged, setPrivacyAcknowledged] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [rawContractText, setRawContractText] = useState<string>("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState("");
  const [documentResult, setDocumentResult] = useState<DocumentResult | null>(null);
  const [currentJobId, setCurrentJobId] = useState("");
  const [pipelineError, setPipelineError] = useState("");
  const [parsedContract, setParsedContract] = useState<ParsedContract | null>(null);
  const operationRef = useRef(0);

  const clearSession = () => {
    operationRef.current++;
    setDocumentResult(null); setCurrentJobId(""); setRawContractText("");
    setParsedContract(null);
    setSelectedClauseId(""); setPipelineError(""); setFeedbackSuccess(null);
    setActiveTab("upload"); setActiveSection("overview"); setAnalyzing(false);
  };

  const openSavedAnalysis = async (jobId: string) => {
    const operation = ++operationRef.current;
    const response = await fetch(`${backendUrl}/v1/jobs/${jobId}/results`, { headers: { "X-API-Key": apiKey.trim() } });
    if (!response.ok) throw new Error("Saved analysis unavailable for this session.");
    const result: DocumentResult = await response.json();
    if (operation !== operationRef.current) return;
    setDocumentResult(result); setCurrentJobId(jobId);
    setRawContractText(result.metadata?.source_text || "");
    setSelectedClauseId(result.scoring_result.clauses[0]?.clause_id || "");
    setActiveTab("results"); setActiveSection("contract-review");
  };

  // Authoritative clause selection in React memory
  const [selectedClauseId, setSelectedClauseId] = useState<string>("");

  // Reviewer feedback
  const [feedbackVerdict, setFeedbackVerdict] = useState<string>("CONFIRM_ANOMALY");
  const [reviewerId, setReviewerId] = useState("reviewer_01");
  const [feedbackProvenance, setFeedbackProvenance] = useState("REAL");
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  // Probe Backend Connectivity
  useEffect(() => {
    let cancelled = false;
    const probe = () => fetch(`${backendUrl}/health`, { signal: AbortSignal.timeout(5000) })
      .then(res => { if (!cancelled) setBackendStatus(res.ok ? "online" : "offline"); })
      .catch(() => { if (!cancelled) setBackendStatus("offline"); });
    void probe();
    const interval = setInterval(probe, 15000);
    return () => { cancelled = true; clearInterval(interval); };
  }, [backendUrl]);

  // Synchronize Section & Tab Navigation
  const handleSelectSection = (section: NavSection) => {
    setActiveSection(section);
    if (section === "overview") setActiveTab("upload");
    else if (section === "contract-review" || section === "analytics") setActiveTab("results");
    else if (section === "explainability") setActiveTab("xai");
    else if (section === "feedback") setActiveTab("feedback");
    else if (section === "robustness-lab") setActiveTab("redteam");
    else if (section === "transparency") setActiveTab("transparency");
  };

  const handleSelectTab = (tab: "upload" | "results" | "xai" | "feedback" | "redteam" | "transparency") => {
    setActiveTab(tab);
    if (tab === "upload") setActiveSection("overview");
    else if (tab === "results") {
      if (activeSection !== "analytics") setActiveSection("contract-review");
    } else if (tab === "xai") setActiveSection("explainability");
    else if (tab === "feedback") setActiveSection("feedback");
    else if (tab === "redteam") setActiveSection("robustness-lab");
    else if (tab === "transparency") setActiveSection("transparency");
  };

  const handleUploadAndAnalyze = async (previewOnly = false, existingDocId?: string) => {
    if ((!file && !existingDocId) || !privacyAcknowledged || !apiKey.trim()) return;

    const operation = ++operationRef.current;
    try {
      setPipelineError(""); setDocumentResult(null); setCurrentJobId(""); setRawContractText("");
      setParsedContract(null);
      setAnalyzing(true);
      setAnalysisStatus("Parsing and securely uploading document…");
      let doc_id = existingDocId;
      if (!doc_id) {
        if (!file) throw new Error("Choose a document first.");
        if (file.size > 10 * 1024 * 1024) throw new Error("File exceeds the 10 MB limit.");
        if (!/\.(txt|pdf|docx)$/i.test(file.name)) throw new Error("Choose a PDF, DOCX or UTF-8 TXT file.");
        const formData = new FormData();
        formData.append("file", file);
        const uploadRes = await fetch(`${backendUrl}/v1/upload`, {
          method: "POST", headers: { "X-API-Key": apiKey.trim() }, body: formData,
        });
        if (!uploadRes.ok) {
          const err = await uploadRes.json();
          throw new Error(err.detail || "Upload failed");
        }
        doc_id = (await uploadRes.json()).doc_id;
      }
      if (operation !== operationRef.current) return;
      const previewRes = await fetch(`${backendUrl}/v1/documents/${doc_id}/clauses`, { headers: { "X-API-Key": apiKey.trim() } });
      if (!previewRes.ok) {
        const error = await previewRes.json();
        throw new Error(error.detail || "Clause preview unavailable.");
      }
      const parsed: ParsedContract = await previewRes.json();
      if (operation !== operationRef.current) return;
      setParsedContract(parsed); setRawContractText(parsed.source_text);
      if (previewOnly) return;
      setAnalysisStatus("Loading local analysis models…");

      const analyzeRes = await fetch(`${backendUrl}/v1/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey.trim(),
        },
        body: JSON.stringify({ doc_id }),
      });

      if (!analyzeRes.ok) {
        const err = await analyzeRes.json();
        throw new Error(err.detail || "Analysis trigger failed");
      }

      const { job_id } = await analyzeRes.json();
      setAnalysisStatus("Analyzing clauses locally…");

      // Poll job
      let completed = false;
      let attempts = 0;
      while (!completed && attempts < 150) {
        if (operation !== operationRef.current) return;
        attempts++;
        await new Promise((r) => setTimeout(r, 2000));
        const statusRes = await fetch(`${backendUrl}/v1/jobs/${job_id}`, {
          headers: { "X-API-Key": apiKey.trim() },
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();
          if (statusData.status === "COMPLETED") {
            completed = true;
          } else if (statusData.status === "FAILED") {
            throw new Error(statusData.error || "Analysis failed");
          }
        } else throw new Error(`Could not check analysis status (${statusRes.status}).`);
      }

      if (!completed) throw new Error("Analysis is taking longer than five minutes. Refresh saved documents later to reopen a completed result.");

      setAnalysisStatus("Retrieving audit report...");
      const resultsRes = await fetch(`${backendUrl}/v1/jobs/${job_id}/results`, {
        headers: { "X-API-Key": apiKey.trim() },
      });

      if (!resultsRes.ok) throw new Error("Failed to retrieve analysis results");

      const resData: DocumentResult = await resultsRes.json();
      if (operation !== operationRef.current) return;
      setDocumentResult(resData);
      setCurrentJobId(job_id);
      setRawContractText(resData.metadata?.source_text || "");
      if (resData.scoring_result.clauses && resData.scoring_result.clauses.length > 0) {
        setSelectedClauseId(resData.scoring_result.clauses[0].clause_id);
      }
      setActiveTab("results");
      setActiveSection("contract-review");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Pipeline error";
      if (operation === operationRef.current) setPipelineError(msg);
    } finally {
      if (operation === operationRef.current) { setAnalyzing(false); setAnalysisStatus(""); }
    }
  };

  const handleSubmitFeedback = async () => {
    if (!documentResult || !selectedClauseId || !apiKey.trim()) return;
    const clause = documentResult.scoring_result.clauses.find((c) => c.clause_id === selectedClauseId);
    if (!clause) return;

    try {
      const payload = {
        doc_id: documentResult.doc_id,
        clause_id: clause.clause_id,
        original_severity: clause.severity,
        reviewer_verdict: feedbackVerdict,
        reviewer_id: reviewerId,
        provenance: feedbackProvenance,
        model_version: "v1",
      };

      const res = await fetch(`${backendUrl}/v1/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey.trim(),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Feedback submission failed");
      const data = await res.json();
      setFeedbackSuccess(`Feedback recorded successfully! ID: ${data.feedback_id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error submitting feedback";
      alert(`Error submitting feedback: ${msg}`);
    }
  };

  return (
    <ThemeProvider>
      <AppShell
        activeSection={activeSection}
        onSelectSection={handleSelectSection}
        backendStatus={backendStatus}
        backendUrl={backendUrl}
        onBackendUrlChange={(value) => { clearSession(); setBackendUrl(value); }}
        apiKey={apiKey}
        onApiKeyChange={(value) => { clearSession(); setApiKey(value); }}
        documentLoaded={!!documentResult}
      >
        <ReleaseTools key={`${backendUrl}:${apiKey}:${currentJobId}`} backendUrl={backendUrl} apiKey={apiKey} jobId={currentJobId} onOpen={openSavedAnalysis} />
        {apiKey && <button className="btn btn-secondary" onClick={() => { clearSession(); setApiKey(""); }}>Sign out and clear document</button>}
        {pipelineError && <div className="caveat-box" role="alert">{pipelineError}</div>}
        {/* In-Workspace Secondary Navigation Strip for 100% Selector Compatibility */}
        <nav className="tab-nav" role="tablist" aria-label="Auditor Navigation">
          <button
            id="tab-upload"
            role="tab"
            aria-selected={activeTab === "upload"}
            className={`tab-btn ${activeTab === "upload" ? "active" : ""}`}
            onClick={() => handleSelectTab("upload")}
          >
            1. Upload &amp; Ingest
          </button>
          <button
            id="tab-results"
            role="tab"
            aria-selected={activeTab === "results"}
            className={`tab-btn ${activeTab === "results" ? "active" : ""}`}
            onClick={() => handleSelectTab("results")}
            disabled={!documentResult}
          >
            2. Coherence Heatmap &amp; Findings
          </button>
          <button
            id="tab-xai"
            role="tab"
            aria-selected={activeTab === "xai"}
            className={`tab-btn ${activeTab === "xai" ? "active" : ""}`}
            onClick={() => handleSelectTab("xai")}
            disabled={!documentResult}
          >
            3. Explainability (XAI)
          </button>
          <button
            id="tab-feedback"
            role="tab"
            aria-selected={activeTab === "feedback"}
            className={`tab-btn ${activeTab === "feedback" ? "active" : ""}`}
            onClick={() => handleSelectTab("feedback")}
            disabled={!documentResult}
          >
            4. Reviewer Feedback
          </button>
          <button
            id="tab-redteam"
            role="tab"
            aria-selected={activeTab === "redteam"}
            className={`tab-btn ${activeTab === "redteam" ? "active" : ""}`}
            onClick={() => handleSelectTab("redteam")}
          >
            5. Robustness Lab
          </button>
          <button
            id="tab-transparency"
            role="tab"
            aria-selected={activeTab === "transparency"}
            className={`tab-btn ${activeTab === "transparency" ? "active" : ""}`}
            onClick={() => handleSelectTab("transparency")}
          >
            6. Transparency &amp; Baselines
          </button>
        </nav>

        {/* SECTION 1 / TAB 1: UPLOAD & INGEST */}
        {activeTab === "upload" && (
          <section className="card" role="tabpanel" aria-labelledby="tab-upload">
            <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem", color: "var(--color-text-primary)" }}>
              Ingest Contract Document
            </h2>

            <div className="caveat-box" style={{ marginBottom: "1.25rem", padding: "1rem" }}>
              <h3 style={{ fontSize: "0.95rem", color: "var(--color-text-primary)", marginBottom: "0.5rem" }}>
                🔒 Confidentiality &amp; Data Retention Disclosure
              </h3>
              <ul style={{ paddingLeft: "1.2rem", fontSize: "0.85rem", color: "var(--color-text-secondary)", lineHeight: 1.6 }}>
                <li><strong>Encryption at Rest:</strong> Uploads are encrypted via Fernet (AES-128-CBC + HMAC-SHA256). Zero contract plaintext is written to persistent disk.</li>
                <li><strong>Data Retention:</strong> Encrypted uploads and saved analyses are removed by the configured retention cleanup (24 hours by default).</li>
                <li><strong>Zero Plaintext Logging:</strong> Server audit logs strictly prohibit recording contract text or client keys.</li>
                <li><strong>Academic Prototype:</strong> Designed for structural coherence research. Not formal legal advice.</li>
              </ul>
            </div>

            <label htmlFor="privacy-consent" style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.5rem", cursor: "pointer", fontSize: "0.9rem" }}>
              <input
                id="privacy-consent"
                type="checkbox"
                checked={privacyAcknowledged}
                onChange={(e) => setPrivacyAcknowledged(e.target.checked)}
              />
              <span style={{ color: "var(--color-text-primary)" }}>
                I acknowledge the privacy &amp; retention notice and consent to encrypted temporary analysis.
              </span>
            </label>

            <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "1.5rem", flexWrap: "wrap" }}>
              <input
                id="file-input"
                aria-label="Upload Contract Document (.txt, .pdf, .docx)"
                type="file"
                accept=".txt,.pdf,.docx"
                disabled={analyzing}
                onChange={(e) => { setFile(e.target.files?.[0] || null); setParsedContract(null); }}
                className="input-field"
                style={{ maxWidth: "400px" }}
              />
              <button
                id="analyze-btn"
                aria-label="Encrypt, Upload & Analyze Contract"
                className="btn"
                disabled={!privacyAcknowledged || !file || !apiKey.trim() || analyzing}
                onClick={() => void handleUploadAndAnalyze()}
              >
                {analyzing ? "Analyzing..." : "🚀 Encrypt, Upload & Analyze"}
              </button>
              <button id="preview-btn" className="btn btn-secondary" disabled={!privacyAcknowledged || !file || !apiKey.trim() || analyzing}
                onClick={() => void handleUploadAndAnalyze(true)}>Parse and preview clauses</button>
            </div>

            <p>PDF, DOCX or UTF-8 TXT. Maximum 10 MB, 100 PDF pages, 250,000 extracted characters and 500 clauses. Scanned PDFs require OCR first.</p>
            {analyzing && <p role="status" aria-live="polite" style={{ color: "var(--color-accent)", fontSize: "0.9rem" }}>{analysisStatus}</p>}
            {parsedContract && <div aria-label="Parsed clause preview" className="card">
              <h3>{parsedContract.clauses.length} parsed clauses</h3>
              <p>Review the extracted text before running the local models. Locations refer to normalized source text.</p>
              <button id="analyze-preview-btn" className="btn" disabled={analyzing || !privacyAcknowledged || !apiKey.trim()}
                onClick={() => void handleUploadAndAnalyze(false, parsedContract.doc_id)}>Analyze this parsed document</button>
              <div style={{ maxHeight: "400px", overflowY: "auto", overflowWrap: "anywhere" }}>
                {parsedContract.clauses.map(c => <details key={c.clause_id}>
                  <summary>Clause {c.sequence_idx + 1} — {c.clause_id}</summary>
                  <p>Source offsets: {c.char_start}–{c.char_end}</p><p style={{ whiteSpace: "pre-wrap" }}>{c.text}</p>
                </details>)}
              </div>
            </div>}
          </section>
        )}

        {/* SECTION 2 & 3 / TAB 2: RESULTS (Contract Review & Analytics) */}
        {activeTab === "results" && !documentResult && (
          activeSection === "analytics" ? (
            <AnalyticsWorkspace
              documentResult={null}
              selectedClauseId=""
              onSelectClauseId={() => {}}
              onNavigateToUpload={() => {
                setActiveSection("overview");
                setActiveTab("upload");
              }}
            />
          ) : (
            <EmptyState
              icon={<BookOpenCheck size={48} />}
              title="No Active Contract in Review"
              description="Please upload and analyze a contract document in Overview to inspect sequence coherence and clause anomalies."
              action={
                <button
                  className="btn"
                  onClick={() => {
                    setActiveSection("overview");
                    setActiveTab("upload");
                  }}
                >
                  <span>Go to Ingestion &amp; Upload</span>
                  <ArrowRight size={16} aria-hidden="true" />
                </button>
              }
            />
          )
        )}

        {activeTab === "results" && documentResult && (
          <section role="tabpanel" aria-labelledby="tab-results">
            <p role="status">{documentResult.metadata?.analysis_state === "NO_FINDINGS" ?
              "No configured detector findings. This does not establish legal correctness or completeness." :
              "Review required. Statistical anomalies and automated rule candidates need human interpretation."}</p>
            {activeSection !== "analytics" ? (
              <>
                {/* KPI Summary Cards for Contract Review Workspace */}
                <div className="grid-kpis" style={{ marginBottom: "1rem" }}>
                  <div className="kpi-card">
                    <div className="kpi-label">Total Clauses</div>
                    <div className="kpi-value">{documentResult.total_clauses}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Total Review Flags</div>
                    <div className="kpi-value" style={{ color: "var(--sev-med-text)" }}>{documentResult.total_flags}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">High Severity</div>
                    <div className="kpi-value" style={{ color: "var(--sev-high-text)" }}>{documentResult.high_severity_count}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Medium Severity</div>
                    <div className="kpi-value" style={{ color: "var(--sev-med-text)" }}>{documentResult.medium_severity_count}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Mean Anomaly Score</div>
                    <div className="kpi-value">{documentResult.scoring_result.mean_combined_score.toFixed(3)}</div>
                  </div>
                </div>

                {/* Split-Screen Review Workspace */}
                <ContractReviewWorkspace
                  documentResult={documentResult}
                  rawContractText={rawContractText}
                  selectedClauseId={selectedClauseId}
                  onSelectClauseId={setSelectedClauseId}
                  backendUrl={backendUrl}
                  apiKey={apiKey}
                  onNavigateToXai={() => {
                    setActiveSection("explainability");
                    setActiveTab("xai");
                  }}
                  onNavigateToFeedback={() => {
                    setActiveSection("feedback");
                    setActiveTab("feedback");
                  }}
                />
              </>
            ) : (
              /* Professional Analytics & Findings Workspace (Phase 4A) */
              <AnalyticsWorkspace
                documentResult={documentResult}
                selectedClauseId={selectedClauseId}
                onSelectClauseId={setSelectedClauseId}
                onNavigateToReview={() => {
                  setActiveSection("contract-review");
                  setActiveTab("results");
                }}
                onNavigateToUpload={() => {
                  setActiveSection("overview");
                  setActiveTab("upload");
                }}
                onNavigateToXai={() => {
                  setActiveSection("explainability");
                  setActiveTab("xai");
                }}
                onNavigateToFeedback={() => {
                  setActiveSection("feedback");
                  setActiveTab("feedback");
                }}
              />
            )}
          </section>
        )}

        {/* SECTION 4 / TAB 3: EXPLAINABILITY (XAI) */}
        {activeTab === "xai" && (
          <section role="tabpanel" aria-labelledby="tab-xai">
            <ExplainabilityWorkspace
              documentResult={documentResult}
              selectedClauseId={selectedClauseId}
              onSelectClauseId={setSelectedClauseId}
              backendUrl={backendUrl}
              apiKey={apiKey}
              onNavigateToReview={() => {
                setActiveSection("contract-review");
                setActiveTab("results");
              }}
              onNavigateToFeedback={() => {
                setActiveSection("feedback");
                setActiveTab("feedback");
              }}
              onNavigateToUpload={() => {
                setActiveSection("overview");
                setActiveTab("upload");
              }}
            />
          </section>
        )}

        {/* SECTION 5 / TAB 4: REVIEWER FEEDBACK */}
        {activeTab === "feedback" && !documentResult && (
          <EmptyState
            icon={<MessageSquareCheck size={48} />}
            title="Feedback Interface Inactive"
            description="Reviewer recalibration requires an analyzed document. Please ingest a contract in Overview first."
            action={
              <button
                className="btn"
                onClick={() => {
                  setActiveSection("overview");
                  setActiveTab("upload");
                }}
              >
                <span>Go to Ingestion &amp; Upload</span>
                <ArrowRight size={16} aria-hidden="true" />
              </button>
            }
          />
        )}

        {activeTab === "feedback" && documentResult && (
          <section className="card" role="tabpanel" aria-labelledby="tab-feedback">
            <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", color: "var(--color-text-primary)" }}>
              Reviewer Recalibration Interface
            </h2>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginBottom: "1.5rem" }}>
              Record reviewer observations for later review. Credentials are self-reported; submitting feedback does not retrain models or change frozen thresholds.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
              <div>
                <label htmlFor="clause-select-fb" style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", display: "block", marginBottom: "0.35rem" }}>
                  Select Anomaly Clause
                </label>
                <select
                  id="clause-select-fb"
                  aria-label="Select Anomaly Clause"
                  value={selectedClauseId}
                  onChange={(e) => setSelectedClauseId(e.target.value)}
                  className="input-field"
                >
                  {documentResult.scoring_result.clauses.map((c) => (
                    <option key={c.clause_id} value={c.clause_id}>
                      § {c.sequence_idx} - Score {c.combined_score.toFixed(2)} ({c.severity})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="feedback-verdict-select" style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", display: "block", marginBottom: "0.35rem" }}>
                  Reviewer Verdict
                </label>
                <select
                  id="feedback-verdict-select"
                  aria-label="Reviewer Verdict"
                  value={feedbackVerdict}
                  onChange={(e) => setFeedbackVerdict(e.target.value)}
                  className="input-field"
                >
                  <option value="CONFIRM_ANOMALY">CONFIRM_ANOMALY (Reviewer agrees with flag)</option>
                  <option value="REJECT_ANOMALY">REJECT_ANOMALY (Reviewer rejects flag)</option>
                </select>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
              <div>
                <label htmlFor="reviewer-id-input" style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", display: "block", marginBottom: "0.35rem" }}>
                  Reviewer Signature ID
                </label>
                <input
                  id="reviewer-id-input"
                  aria-label="Reviewer Signature ID"
                  type="text"
                  value={reviewerId}
                  onChange={(e) => setReviewerId(e.target.value)}
                  className="input-field"
                />
              </div>
              <div>
                <label htmlFor="feedback-provenance-select" style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", display: "block", marginBottom: "0.35rem" }}>
                  Provenance
                </label>
                <select
                  id="feedback-provenance-select"
                  aria-label="Feedback Provenance"
                  value={feedbackProvenance}
                  onChange={(e) => setFeedbackProvenance(e.target.value)}
                  className="input-field"
                >
                  <option value="REAL">REAL (Human feedback; credentials not verified)</option>
                  <option value="SYNTHETIC_TEST">SYNTHETIC_TEST (Test observation)</option>
                </select>
              </div>
            </div>

            <button
              id="submit-feedback-btn"
              aria-label="Submit Feedback to API"
              className="btn"
              onClick={handleSubmitFeedback}
              disabled={!apiKey.trim()}
            >
              💾 Submit Feedback to API
            </button>

            {feedbackSuccess && (
              <p id="feedback-success-msg" role="status" aria-live="polite" style={{ marginTop: "1rem", color: "var(--color-success)", fontSize: "0.9rem" }}>
                {feedbackSuccess}
              </p>
            )}
          </section>
        )}

        {/* SECTION 5 / TAB 5: ROBUSTNESS LAB (RED-TEAM) */}
        {activeTab === "redteam" && (
          <section role="tabpanel" aria-labelledby="tab-redteam">
            <RedTeamWorkspace
              backendUrl={backendUrl}
              apiKey={apiKey}
              activeDocId={documentResult?.doc_id}
              activeDocClauses={documentResult?.scoring_result?.clauses?.map((c) => ({
                clause_id: c.clause_id,
                sequence_idx: c.sequence_idx,
                text: documentResult?.metadata?.clause_inventory?.find(item => item.clause_id === c.clause_id)?.text || c.text_preview,
              }))}
            />
          </section>
        )}

        {/* SECTION 6 / TAB 6: TRANSPARENCY & BENCHMARKS */}
        {activeTab === "transparency" && (
          <section className="card" role="tabpanel" aria-labelledby="tab-transparency">
            <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", color: "var(--color-text-primary)" }}>
              Model Transparency &amp; Empirical Benchmarks
            </h2>
            <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginBottom: "1.5rem" }}>
              Historical Prompt 14 development results, shown for research context. These are not independent evidence of legal correctness.
            </p>
            <div className="caveat-box"><strong>Exploratory evidence only.</strong> Phase 4D-C-A found compromised preregistration and invalid order transformations. Phase 4D-D-A retained 9 directional candidates and 15 eligible negatives for development. Independent human annotation and unseen-family evaluation remain pending.</div>

            <div className="grid-kpis">
              <div className="kpi-card">
                <div className="kpi-label">Kendall&apos;s Tau (LEDGAR)</div>
                <div className="kpi-value">-0.0285</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>95% CI: [-0.125, +0.073]</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Clean SEC FPR (High)</div>
                <div className="kpi-value">1.18%</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>95% CI: [0.57%, 2.41%]</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Clean SEC FPR (Med+High)</div>
                <div className="kpi-value">44.54%</div>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>95% CI: [40.59%, 48.55%]</div>
              </div>
            </div>

            <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--color-border)", textAlign: "left", color: "var(--color-text-secondary)" }}>
                  <th style={{ padding: "0.5rem" }}>Model Architecture</th>
                  <th style={{ padding: "0.5rem" }}>Accuracy</th>
                  <th style={{ padding: "0.5rem" }}>F1 Score</th>
                  <th style={{ padding: "0.5rem" }}>Kendall&apos;s Tau</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>Dual-Channel Auditor (Our Model)</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>50.0%</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.00</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>-0.2100</td>
                </tr>
                <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>Logistic Regression Baseline</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>55.0%</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.6087</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>+0.0816</td>
                </tr>
                <tr>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>Majority-Vote Baseline</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>50.0%</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.00</td>
                  <td style={{ padding: "0.5rem", color: "var(--color-text-primary)" }}>0.0000</td>
                </tr>
              </tbody>
            </table>
          </section>
        )}
      </AppShell>
    </ThemeProvider>
  );
}
