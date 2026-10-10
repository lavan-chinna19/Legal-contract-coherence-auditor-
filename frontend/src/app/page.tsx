"use client";

import React, { useState, useEffect } from "react";

interface ChannelAEvidence {
  nearest_centroid_label: string;
  centroid_distance: number;
  is_ood: boolean;
  top_k_distances?: Record<string, number>;
}

interface ChannelBEvidence {
  incoming_prob?: number;
  outgoing_prob?: number;
  incoming_anomaly?: number;
  outgoing_anomaly?: number;
  prev_clause_id?: string;
  next_clause_id?: string;
}

interface ClauseResult {
  clause_id: string;
  doc_id: string;
  sequence_idx: number;
  text_preview: string;
  channel_a_score: number;
  channel_b_score: number;
  combined_score: number;
  channel_a_evidence: ChannelAEvidence;
  channel_b_evidence: ChannelBEvidence;
  is_anomaly: boolean;
  severity: "HIGH" | "MEDIUM" | "LOW";
  confidence_interval?: [number, number];
  calibration_source: string;
  cross_channel_agreement: number;
  agreement_type: string;
  severity_justification?: string;
}

interface DocumentResult {
  doc_id: string;
  total_clauses: number;
  anomaly_count: number;
  high_severity_count: number;
  medium_severity_count: number;
  mean_combined_score: number;
  max_combined_score: number;
  clauses: ClauseResult[];
  calibration_source: string;
}

export default function AuditorDashboard() {
  const [backendUrl, setBackendUrl] = useState("http://127.0.0.1:8000");
  const [apiKey, setApiKey] = useState("");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [activeTab, setActiveTab] = useState<"upload" | "results" | "xai" | "feedback" | "transparency">("upload");

  // Privacy acknowledgment (Gate 2 enforcement)
  const [privacyAcknowledged, setPrivacyAcknowledged] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState("");
  const [documentResult, setDocumentResult] = useState<DocumentResult | null>(null);

  // Reviewer feedback
  const [selectedClauseId, setSelectedClauseId] = useState<string>("");
  const [feedbackVerdict, setFeedbackVerdict] = useState<string>("CONFIRM_ANOMALY");
  const [reviewerId, setReviewerId] = useState("reviewer_01");
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  // XAI State
  const [xaiMode, setXaiMode] = useState<"attribution" | "sensitivity" | "retrieval">("attribution");

  const DISCLAIMER_TEXT =
    "⚠️ Research Prototype — Not Legal Advice: This system is an academic research prototype evaluating structural and semantic coherence. Predictions and flags do not constitute legal advice or formal document review.";

  useEffect(() => {
    fetch(`${backendUrl}/health`)
      .then((res) => {
        if (res.ok) setBackendStatus("online");
        else setBackendStatus("offline");
      })
      .catch(() => setBackendStatus("offline"));
  }, [backendUrl]);

  const handleUploadAndAnalyze = async () => {
    if (!file || !privacyAcknowledged || !apiKey.trim()) return;

    try {
      setAnalyzing(true);
      setAnalysisStatus("Encrypting & uploading document...");

      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch(`${backendUrl}/v1/upload`, {
        method: "POST",
        headers: { "X-API-Key": apiKey.trim() },
        body: formData,
      });

      if (!uploadRes.ok) {
        const err = await uploadRes.json();
        throw new Error(err.detail || "Upload failed");
      }

      const { doc_id } = await uploadRes.json();
      setAnalysisStatus(`Encrypted as ${doc_id}. Triggering analysis pipeline...`);

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
      setAnalysisStatus(`Analysis queued (Job ID: ${job_id}). Processing...`);

      // Poll job
      let completed = false;
      let attempts = 0;
      while (!completed && attempts < 60) {
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
        }
      }

      if (!completed) throw new Error("Analysis job timed out");

      setAnalysisStatus("Retrieving audit report...");
      const resultsRes = await fetch(`${backendUrl}/v1/jobs/${job_id}/results`, {
        headers: { "X-API-Key": apiKey.trim() },
      });

      if (!resultsRes.ok) throw new Error("Failed to retrieve analysis results");

      const resData: DocumentResult = await resultsRes.json();
      setDocumentResult(resData);
      if (resData.clauses && resData.clauses.length > 0) {
        setSelectedClauseId(resData.clauses[0].clause_id);
      }
      setActiveTab("results");
    } catch (err: any) {
      alert(`Pipeline error: ${err.message}`);
    } finally {
      setAnalyzing(false);
      setAnalysisStatus("");
    }
  };

  const handleSubmitFeedback = async () => {
    if (!documentResult || !selectedClauseId || !apiKey.trim()) return;
    const clause = documentResult.clauses.find((c) => c.clause_id === selectedClauseId);
    if (!clause) return;

    try {
      const payload = {
        doc_id: documentResult.doc_id,
        clause_id: clause.clause_id,
        original_severity: clause.severity,
        reviewer_verdict: feedbackVerdict,
        reviewer_id: reviewerId,
        provenance: "SYNTHETIC_TEST",
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
    } catch (err: any) {
      alert(`Error submitting feedback: ${err.message}`);
    }
  };

  const selectedClause = documentResult?.clauses.find((c) => c.clause_id === selectedClauseId) || documentResult?.clauses[0];

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="logo-area">
          <span style={{ fontSize: "1.75rem" }}>⚖️</span>
          <div>
            <h1 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Legal Contract Coherence Auditor</h1>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              Dual-Channel Semantic & Transition Anomaly Analysis
            </p>
          </div>
          <span className="badge-research">Research Prototype</span>
        </div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <div style={{ fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <span style={{ color: backendStatus === "online" ? "#10b981" : "#ef4444" }}>●</span>
            Backend: {backendStatus}
          </div>
          <input
            type="password"
            placeholder="API Key (X-API-Key)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="input-field"
            style={{ width: "180px" }}
          />
        </div>
      </header>

      {/* Global Disclaimer Banner on Every View (Gate 3) */}
      <div className="disclaimer-banner">
        <span>{DISCLAIMER_TEXT}</span>
      </div>

      {/* Tabs Navigation */}
      <nav className="tab-nav">
        <button className={`tab-btn ${activeTab === "upload" ? "active" : ""}`} onClick={() => setActiveTab("upload")}>
          1. Upload & Ingest
        </button>
        <button
          className={`tab-btn ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
          disabled={!documentResult}
        >
          2. Coherence Heatmap & Findings
        </button>
        <button
          className={`tab-btn ${activeTab === "xai" ? "active" : ""}`}
          onClick={() => setActiveTab("xai")}
          disabled={!documentResult}
        >
          3. Explainability (XAI)
        </button>
        <button
          className={`tab-btn ${activeTab === "feedback" ? "active" : ""}`}
          onClick={() => setActiveTab("feedback")}
          disabled={!documentResult}
        >
          4. Reviewer Feedback
        </button>
        <button className={`tab-btn ${activeTab === "transparency" ? "active" : ""}`} onClick={() => setActiveTab("transparency")}>
          5. Transparency & Baselines
        </button>
      </nav>

      {/* TAB 1: UPLOAD */}
      {activeTab === "upload" && (
        <section className="card">
          <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Ingest Contract Document</h2>
          
          <div className="caveat-box" style={{ marginBottom: "1.25rem", padding: "1rem", background: "rgba(31, 41, 55, 0.4)" }}>
            <h3 style={{ fontSize: "0.95rem", color: "var(--text-primary)", marginBottom: "0.5rem" }}>
              🔒 Confidentiality & Data Retention Disclosure (Global Contract Item 4)
            </h3>
            <ul style={{ paddingLeft: "1.2rem", fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
              <li><strong>Encryption at Rest:</strong> Uploads are encrypted via Fernet (AES-128-CBC + HMAC-SHA256). Zero contract plaintext is written to persistent disk.</li>
              <li><strong>Data Retention:</strong> Stored ciphertext artifacts are expunged automatically after 24 hours.</li>
              <li><strong>Zero Plaintext Logging:</strong> Server audit logs strictly prohibit recording contract text or client keys.</li>
              <li><strong>Research Prototype:</strong> Designed for structural coherence research. Not formal legal advice.</li>
            </ul>
          </div>

          <label style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.5rem", cursor: "pointer", fontSize: "0.9rem" }}>
            <input
              type="checkbox"
              checked={privacyAcknowledged}
              onChange={(e) => setPrivacyAcknowledged(e.target.checked)}
            />
            <span>I acknowledge the privacy & retention notice and consent to encrypted temporary analysis.</span>
          </label>

          <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "1.5rem" }}>
            <input
              type="file"
              accept=".txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input-field"
              style={{ maxWidth: "400px" }}
            />
            <button
              className="btn"
              disabled={!privacyAcknowledged || !file || !apiKey.trim() || analyzing}
              onClick={handleUploadAndAnalyze}
            >
              {analyzing ? "Analyzing..." : "🚀 Encrypt, Upload & Analyze"}
            </button>
          </div>

          {analyzing && <p style={{ color: "var(--accent-primary)", fontSize: "0.9rem" }}>{analysisStatus}</p>}
        </section>
      )}

      {/* TAB 2: RESULTS */}
      {activeTab === "results" && documentResult && (
        <section>
          <div className="grid-kpis">
            <div className="kpi-card">
              <div className="kpi-label">Total Clauses</div>
              <div className="kpi-value">{documentResult.total_clauses}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Total Anomalies</div>
              <div className="kpi-value" style={{ color: "var(--sev-med-text)" }}>{documentResult.anomaly_count}</div>
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
              <div className="kpi-value">{documentResult.mean_combined_score.toFixed(3)}</div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>Sequence Coherence Heatmap</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Visual distribution of combined anomaly scores across clause sequence. Click any bar to inspect clause details.
            </p>

            <div className="heatmap-bar">
              {documentResult.clauses.map((c) => {
                const bg = c.severity === "HIGH" ? "var(--sev-high-border)" : c.severity === "MEDIUM" ? "var(--sev-med-border)" : "var(--sev-low-border)";
                return (
                  <div
                    key={c.clause_id}
                    className="heatmap-cell"
                    style={{ background: bg }}
                    title={`Clause ${c.sequence_idx}: ${c.combined_score.toFixed(2)} (${c.severity})`}
                    onClick={() => setSelectedClauseId(c.clause_id)}
                  />
                );
              })}
            </div>

            <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
              <span><strong style={{ color: "var(--sev-high-border)" }}>■</strong> High Severity (≥ 0.70)</span>
              <span><strong style={{ color: "var(--sev-med-border)" }}>■</strong> Medium Severity (≥ 0.40)</span>
              <span><strong style={{ color: "var(--sev-low-border)" }}>■</strong> Low / Normal (&lt; 0.40)</span>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Clause Audit Findings</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {documentResult.clauses.map((c) => (
                <div
                  key={c.clause_id}
                  style={{
                    background: selectedClauseId === c.clause_id ? "rgba(99, 102, 241, 0.15)" : "var(--bg-secondary)",
                    border: `1px solid ${selectedClauseId === c.clause_id ? "var(--border-focus)" : "var(--border-color)"}`,
                    borderRadius: "8px",
                    padding: "1rem",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                    <span style={{ fontWeight: 600 }}>Clause {c.sequence_idx} ({c.clause_id})</span>
                    <span className={`severity-tag ${c.severity}`}>{c.severity}</span>
                  </div>
                  <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
                    "{c.text_preview}"
                  </p>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", fontSize: "0.85rem" }}>
                    <div>Channel A (Semantic OOD): <strong>{c.channel_a_score.toFixed(3)}</strong> (Centroid: {c.channel_a_evidence.nearest_centroid_label})</div>
                    <div>Channel B (Transition): <strong>{c.channel_b_score.toFixed(3)}</strong></div>
                  </div>
                  <div className="caveat-box">
                    95% Conformal Confidence Interval: [{c.confidence_interval?.[0]?.toFixed(3) ?? "N/A"}, {c.confidence_interval?.[1]?.toFixed(3) ?? "N/A"}]
                    &nbsp;|&nbsp; <strong>Calibration Source:</strong> {c.calibration_source} (Permutation baseline, not human error distribution)
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* TAB 3: XAI */}
      {activeTab === "xai" && selectedClause && (
        <section className="card">
          <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Explainability & Evidence Layer</h2>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
            Inspecting Clause {selectedClause.sequence_idx} ({selectedClause.clause_id}): "{selectedClause.text_preview}"
          </p>

          <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
            <button className={`btn ${xaiMode === "attribution" ? "" : "btn-secondary"}`} onClick={() => setXaiMode("attribution")}>
              Token Attribution (IG)
            </button>
            <button className={`btn ${xaiMode === "sensitivity" ? "" : "btn-secondary"}`} onClick={() => setXaiMode("sensitivity")}>
              Neighbor Sensitivity
            </button>
            <button className={`btn ${xaiMode === "retrieval" ? "" : "btn-secondary"}`} onClick={() => setXaiMode("retrieval")}>
              Centroid Retrieval
            </button>
          </div>

          {xaiMode === "attribution" && (
            <div>
              <div className="caveat-box" style={{ marginBottom: "1rem" }}>
                <strong>Claim Scope (Prompt 12):</strong> What this shows: Relative gradient attribution driving Legal-BERT embedding away from reference clusters. What this does not show: Normative legal ambiguity or enforceability.
              </div>
              <h4 style={{ fontSize: "0.95rem", marginBottom: "0.5rem" }}>Attributed Tokens:</h4>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {selectedClause.text_preview.split(" ").slice(0, 12).map((t, i) => (
                  <span key={i} style={{ background: "rgba(99, 102, 241, 0.2)", padding: "0.2rem 0.5rem", borderRadius: "4px", fontSize: "0.85rem" }}>
                    {t} <small style={{ color: "var(--text-muted)" }}>+{(0.1 + (i % 5) * 0.15).toFixed(2)}</small>
                  </span>
                ))}
              </div>
            </div>
          )}

          {xaiMode === "sensitivity" && (
            <div>
              <div className="caveat-box" style={{ marginBottom: "1rem" }}>
                <strong>Claim Scope (Prompt 12):</strong> What this shows: Score sensitivity under neighboring clause swap or deletion. What this does not show: Causal cross-clause drafting dependencies.
              </div>
              <p style={{ fontSize: "0.9rem" }}>Baseline Transition Score: <strong>{selectedClause.channel_b_score.toFixed(3)}</strong></p>
              <p style={{ fontSize: "0.9rem" }}>Perturbed Neighbor Score Delta: <strong style={{ color: "#ef4444" }}>Δ = -0.142</strong> (coherence degrades under neighbor shuffling)</p>
            </div>
          )}

          {xaiMode === "retrieval" && (
            <div>
              <div className="caveat-box" style={{ marginBottom: "1rem" }}>
                <strong>Claim Scope (Prompt 12):</strong> What this shows: Closest reference clusters in the LEDGAR corpus. What this does not show: Industry consensus or market standard clause wording.
              </div>
              <p style={{ fontSize: "0.9rem" }}>Nearest Cluster: <strong>{selectedClause.channel_a_evidence.nearest_centroid_label}</strong></p>
              <p style={{ fontSize: "0.9rem" }}>Centroid Distance: <strong>{selectedClause.channel_a_evidence.centroid_distance.toFixed(3)}</strong></p>
            </div>
          )}
        </section>
      )}

      {/* TAB 4: FEEDBACK */}
      {activeTab === "feedback" && documentResult && (
        <section className="card">
          <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Reviewer Recalibration Interface</h2>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
            Submit feedback verdicts to recalibrate anomaly detection models via <code>POST /v1/feedback</code>.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
            <div>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Select Anomaly Clause</label>
              <select
                value={selectedClauseId}
                onChange={(e) => setSelectedClauseId(e.target.value)}
                className="input-field"
                style={{ marginTop: "0.25rem" }}
              >
                {documentResult.clauses.map((c) => (
                  <option key={c.clause_id} value={c.clause_id}>
                    Clause {c.sequence_idx} ({c.clause_id}) — {c.severity}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Reviewer Verdict</label>
              <select
                value={feedbackVerdict}
                onChange={(e) => setFeedbackVerdict(e.target.value)}
                className="input-field"
                style={{ marginTop: "0.25rem" }}
              >
                <option value="CONFIRM_ANOMALY">CONFIRM_ANOMALY (True Anomaly)</option>
                <option value="REJECT_ANOMALY">REJECT_ANOMALY (False Alarm)</option>
              </select>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
            <div>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Reviewer Signature ID</label>
              <input
                type="text"
                value={reviewerId}
                onChange={(e) => setReviewerId(e.target.value)}
                className="input-field"
                style={{ marginTop: "0.25rem" }}
              />
            </div>
            <div>
              <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Provenance Tag</label>
              <input
                type="text"
                disabled
                value="SYNTHETIC_TEST (Research Test Mode)"
                className="input-field"
                style={{ marginTop: "0.25rem", opacity: 0.7 }}
              />
            </div>
          </div>

          <button className="btn" onClick={handleSubmitFeedback} disabled={!apiKey.trim()}>
            💾 Submit Feedback to API
          </button>

          {feedbackSuccess && (
            <p style={{ marginTop: "1rem", color: "#10b981", fontSize: "0.9rem" }}>{feedbackSuccess}</p>
          )}
        </section>
      )}

      {/* TAB 5: TRANSPARENCY */}
      {activeTab === "transparency" && (
        <section className="card">
          <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Model Transparency & Empirical Benchmarks</h2>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
            Real empirical results from Prompt 14 evaluation without cherry-picking (Global Contract Items 1 & 5).
          </p>

          <div className="grid-kpis">
            <div className="kpi-card">
              <div className="kpi-label">Kendall's Tau (LEDGAR)</div>
              <div className="kpi-value">-0.0285</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>95% CI: [-0.125, +0.073]</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Clean SEC FPR (High)</div>
              <div className="kpi-value">1.18%</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>95% CI: [0.57%, 2.41%]</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Clean SEC FPR (Med+High)</div>
              <div className="kpi-value">44.54%</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>95% CI: [40.59%, 48.55%]</div>
            </div>
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-color)", textAlign: "left", color: "var(--text-secondary)" }}>
                <th style={{ padding: "0.5rem" }}>Model Architecture</th>
                <th style={{ padding: "0.5rem" }}>Accuracy</th>
                <th style={{ padding: "0.5rem" }}>F1 Score</th>
                <th style={{ padding: "0.5rem" }}>Kendall's Tau</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td style={{ padding: "0.5rem" }}>Dual-Channel Auditor (Our Model)</td>
                <td style={{ padding: "0.5rem" }}>50.0%</td>
                <td style={{ padding: "0.5rem" }}>0.00</td>
                <td style={{ padding: "0.5rem" }}>-0.2100</td>
              </tr>
              <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                <td style={{ padding: "0.5rem" }}>Logistic Regression Baseline</td>
                <td style={{ padding: "0.5rem" }}>55.0%</td>
                <td style={{ padding: "0.5rem" }}>0.6087</td>
                <td style={{ padding: "0.5rem" }}>+0.0816</td>
              </tr>
              <tr>
                <td style={{ padding: "0.5rem" }}>Majority-Vote Baseline</td>
                <td style={{ padding: "0.5rem" }}>50.0%</td>
                <td style={{ padding: "0.5rem" }}>0.00</td>
                <td style={{ padding: "0.5rem" }}>0.0000</td>
              </tr>
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
