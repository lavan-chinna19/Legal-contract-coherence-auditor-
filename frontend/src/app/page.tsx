"use client";
import { useEffect, useRef, useState } from "react";
import { FileText, Upload, ArrowRight } from "lucide-react";
import { AppShell } from "../components/layout/AppShell";
import { NavSection } from "../components/layout/SidebarNav";
import { ThemeProvider } from "../components/layout/ThemeContext";
import { EngineSettings } from "../components/audit/EngineSettings";
import { WorkspaceTabs } from "../components/audit/WorkspaceTabs";
import { FindingGroups } from "../components/audit/FindingGroups";
import { ReferenceCheck } from "../components/audit/ReferenceCheck";
import { ModelEvaluation } from "../components/audit/ModelEvaluation";
import { ReleaseTools } from "../components/ReleaseTools";
import { ContractReviewWorkspace } from "../components/review/ContractReviewWorkspace";
import { AnalyticsWorkspace } from "../components/analytics";
import { ExplainabilityWorkspace } from "../components/explainability";
import { RedTeamWorkspace } from "../components/redteam";
import { LearnedCompatibilityWorkspace } from "../components/flow/LearnedCompatibilityWorkspace";
import type { DocumentResult, DependencyGraphResult } from "../components/review/types";
import { auditReviewState, engineIsLocal, normalizeEngineUrl, requestError } from "../lib/workflow";
interface ParsedContract { doc_id: string; source_text: string; clauses: { clause_id: string; sequence_idx: number; text: string; char_start: number; char_end: number }[] }
const RESULT_VIEWS = [{ id: "findings", label: "Findings" }, { id: "review", label: "Clause review" }, { id: "analytics", label: "Analytics" }, { id: "explanations", label: "Explanations" }, { id: "references", label: "Reference checks" }] as const;
const RESEARCH_VIEWS = [{ id: "evaluation", label: "Model evaluation" }, { id: "compatibility", label: "Compatibility map" }, { id: "robustness", label: "Robustness testing" }] as const;
type ResultView = typeof RESULT_VIEWS[number]["id"];
type ResearchView = typeof RESEARCH_VIEWS[number]["id"];
export default function AuditorDashboard() {
  const [backendUrl, setBackendUrl] = useState(process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8010");
  const [apiKey, setApiKey] = useState("");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [section, setSection] = useState<NavSection>("new-audit"), [resultView, setResultView] = useState<ResultView>("findings"), [researchView, setResearchView] = useState<ResearchView>("evaluation");
  const [privacy, setPrivacy] = useState(false), [file, setFile] = useState<File | null>(null), [documentName, setDocumentName] = useState("");
  const [parsed, setParsed] = useState<ParsedContract | null>(null), [result, setResult] = useState<DocumentResult | null>(null), [jobId, setJobId] = useState("");
  const [selectedClauseId, setSelectedClauseId] = useState(""), [graph, setGraph] = useState<DependencyGraphResult | null>(null);
  const [busy, setBusy] = useState(false), [progress, setProgress] = useState(""), [error, setError] = useState("");
  const [verdict, setVerdict] = useState("CONFIRM_ANOMALY"), [reviewerId, setReviewerId] = useState(""), [provenance, setProvenance] = useState("REAL"), [feedbackStatus, setFeedbackStatus] = useState(""), [feedbackBusy, setFeedbackBusy] = useState(false);
  const [session, setSession] = useState(0);
  const generation = useRef(0), analysisController = useRef<AbortController | null>(null);
  function clearDocument() {
    generation.current++; analysisController.current?.abort(); setResult(null); setParsed(null); setJobId(""); setGraph(null); setSelectedClauseId(""); setDocumentName(""); setFile(null); setError(""); setProgress(""); setBusy(false); setReviewerId(""); setFeedbackStatus(""); setFeedbackBusy(false); setVerdict("CONFIRM_ANOMALY"); setProvenance("REAL"); setResultView("findings");
  }
  function connect(url: string, key: string) { clearDocument(); setPrivacy(false); setBackendUrl(url); setApiKey(key); setSession(n => n + 1); setSection("new-audit"); }
  function disconnect() { clearDocument(); setApiKey(""); setPrivacy(false); setSession(n => n + 1); }
  useEffect(() => {
    let cancelled = false; const controller = new AbortController();
    async function probe() {
      try { const url = normalizeEngineUrl(backendUrl); const r = await fetch(`${url}/health`, { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(5000)]), cache: "no-store", redirect: "error" }); if (!cancelled) setBackendStatus(r.ok ? "online" : "offline"); }
      catch { if (!cancelled) setBackendStatus("offline"); }
    }
    void probe(); const interval = setInterval(probe, 15000); return () => { cancelled = true; controller.abort(); clearInterval(interval); };
  }, [backendUrl]);
  useEffect(() => () => analysisController.current?.abort(), []);
  async function checked(path: string, options?: RequestInit, signal?: AbortSignal) {
    const response = await fetch(`${backendUrl}${path}`, { ...options, signal, redirect: "error", cache: "no-store", headers: { "X-API-Key": apiKey, ...options?.headers } });
    if (!response.ok) throw new Error(await requestError(response)); return response;
  }
  function showResult(data: DocumentResult, id: string, name: string) { setResult(data); setJobId(id); setDocumentName(name); setSelectedClauseId(data.scoring_result.clauses[0]?.clause_id || ""); setGraph(data.metadata?.dependency_graph || null); setResultView("findings"); setSection("audit-results"); }
  async function preview() {
    if (!file || !privacy || !apiKey || busy) return;
    const operation = ++generation.current; analysisController.current?.abort(); const controller = new AbortController(); analysisController.current = controller;
    setBusy(true); setError(""); setProgress("Uploading and extracting clauses…"); setParsed(null);
    try {
      if (file.size > 10 * 1024 * 1024) throw new Error("File exceeds the 10 MB limit.");
      if (!/\.(txt|pdf|docx)$/i.test(file.name)) throw new Error("Choose a PDF, DOCX or UTF-8 TXT file.");
      const data = new FormData(); data.append("file", file);
      const upload = await (await checked("/v1/upload", { method: "POST", body: data }, controller.signal)).json();
      const extracted = await (await checked(`/v1/documents/${upload.doc_id}/clauses`, undefined, controller.signal)).json();
      if (operation === generation.current) { setParsed(extracted); setDocumentName(file.name); }
    } catch (e) { if (operation === generation.current) setError(e instanceof Error ? e.message : "Could not extract this document."); }
    finally { if (operation === generation.current) { setBusy(false); setProgress(""); } }
  }
  async function analyze() {
    if (!parsed || !privacy || !apiKey || busy) return;
    const operation = ++generation.current; analysisController.current?.abort(); const controller = new AbortController(); analysisController.current = controller;
    setBusy(true); setError(""); setProgress("Starting local analysis…");
    try {
      const started = await (await checked("/v1/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ doc_id: parsed.doc_id }) }, controller.signal)).json();
      let completed = false;
      for (let attempt = 0; attempt < 150; attempt++) {
        await new Promise(resolve => setTimeout(resolve, 2000)); if (operation !== generation.current) return;
        const state = await (await checked(`/v1/jobs/${started.job_id}`, undefined, controller.signal)).json();
        if (state.status === "FAILED") throw new Error(state.error || "Analysis failed. Try again.");
        if (state.status === "COMPLETED") { completed = true; break; }
        setProgress("Analyzing clauses locally. You can keep reviewing the preview.");
      }
      if (!completed) throw new Error("Analysis is taking longer than five minutes. Check Reports & History later for a completed result.");
      const data = await (await checked(`/v1/jobs/${started.job_id}/results`, undefined, controller.signal)).json();
      if (operation === generation.current) showResult(data, started.job_id, documentName);
    } catch (e) { if (operation === generation.current) setError(e instanceof Error ? e.message : "Analysis failed."); }
    finally { if (operation === generation.current) { setBusy(false); setProgress(""); } }
  }
  async function openSaved(id: string, name: string) {
    const operation = ++generation.current; analysisController.current?.abort(); const controller = new AbortController(); analysisController.current = controller;
    const data = await (await checked(`/v1/jobs/${id}/results`, undefined, controller.signal)).json();
    if (operation === generation.current) { setParsed(null); setFile(null); setFeedbackStatus(""); setBusy(false); setProgress(""); showResult(data, id, name); }
  }
  async function feedback(e: React.FormEvent) {
    e.preventDefault(); if (!result || !selectedClauseId || !apiKey || feedbackBusy) return;
    const clause = result.scoring_result.clauses.find(c => c.clause_id === selectedClauseId); if (!clause) return;
    const operation = generation.current; setFeedbackBusy(true); setFeedbackStatus("");
    try {
      await checked("/v1/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ doc_id: result.doc_id, clause_id: clause.clause_id, original_severity: clause.severity, reviewer_verdict: verdict, reviewer_id: reviewerId.trim(), provenance, model_version: "v1" }) });
      if (operation === generation.current) setFeedbackStatus("Reviewer feedback saved.");
    } catch (e) { if (operation === generation.current) setError(e instanceof Error ? e.message : "Feedback could not be saved."); }
    finally { if (operation === generation.current) setFeedbackBusy(false); }
  }
  const goReview = (id?: string) => { if (id) setSelectedClauseId(id); setResultView("review"); setSection("audit-results"); };
  const goExplain = () => { setResultView("explanations"); setSection("audit-results"); };
  const needConnection = <div className="setup-notice"><p>Connect your local engine in Settings to start or reopen an audit.</p><button className="btn btn-secondary" onClick={() => setSection("settings")}>Set up local engine<ArrowRight size={15} aria-hidden="true" /></button></div>;
  return <ThemeProvider><AppShell activeSection={section} onSelectSection={setSection} backendStatus={backendStatus} authenticated={!!apiKey} localEngine={engineIsLocal(backendUrl)}>
    {error && <div className="inline-error" role="alert"><span>{error}</span><button className="btn btn-secondary" onClick={() => setError("")}>Dismiss</button></div>}
    {busy && section !== "new-audit" && <p role="status">{progress} <button className="evidence-link" onClick={() => setSection("new-audit")}>Open current audit</button></p>}
    {section === "settings" && <EngineSettings key={session} backendUrl={backendUrl} connected={!!apiKey} onConnect={connect} onDisconnect={disconnect} />}
    {section === "new-audit" && <div className="stack">
      {!apiKey && needConnection}
      <ol className="workflow-steps" aria-label="Audit workflow"><li aria-current={!parsed && !result ? "step" : undefined}>1. Upload</li><li aria-current={parsed && !result ? "step" : undefined}>2. Preview</li><li>3. Analyze</li><li>4. Review & export</li></ol>
      <section className="card upload-card"><h2>Choose a document</h2><p>PDF, DOCX or UTF-8 TXT, up to 10 MB. Text-based PDFs only.</p>
        <label className="consent-row" htmlFor="privacy-consent"><input id="privacy-consent" type="checkbox" checked={privacy} onChange={e => setPrivacy(e.target.checked)} />I consent to encrypted temporary analysis under the privacy and retention notice.</label>
        <details className="privacy-details"><summary>Privacy, retention and file limits</summary><p>Uploads, filenames and saved results are encrypted on the engine. Retention cleanup defaults to 24 hours. Contract text and keys are not logged. Exported reports contain sensitive excerpts.</p><p>Maximum 100 PDF pages, 250,000 extracted characters and 500 clauses. Scanned PDFs need OCR first. Rule and model findings require human review.</p></details>
        <div className="upload-control"><label htmlFor="file-input"><FileText size={26} aria-hidden="true" /><span>{file ? file.name : "Select a contract"}</span></label><input id="file-input" type="file" accept=".txt,.pdf,.docx" aria-label="Choose contract file" disabled={busy} onChange={e => { const next = e.target.files?.[0] || null; clearDocument(); setFile(next); }} /></div>
        <button id="preview-btn" className="btn" disabled={!apiKey || !privacy || !file || busy} onClick={() => void preview()}><Upload size={16} aria-hidden="true" />{busy && !parsed ? "Preparing preview…" : "Upload and preview"}</button>
        {busy && <p role="status" aria-live="polite">{progress}</p>}
      </section>
      {parsed && <section className="card" aria-label="Clause preview"><div className="section-row"><div><h2>{documentName}</h2><p>{parsed.clauses.length} extracted clauses · Review before analysis.</p></div><button id="analyze-preview-btn" className="btn" disabled={busy || !privacy || !apiKey} onClick={() => void analyze()}>{busy ? "Analyzing…" : "Analyze document"}<ArrowRight size={16} aria-hidden="true" /></button></div>
        <div className="clause-preview">{parsed.clauses.map(c => <details key={c.clause_id}><summary>Clause {c.sequence_idx + 1}</summary><p className="source-text">{c.text}</p><details><summary>Source details</summary><p>{c.clause_id} · Normalized offsets {c.char_start}–{c.char_end}</p></details></details>)}</div></section>}
    </div>}
    {section === "audit-results" && (!result ? <section className="card empty-workspace"><h2>No audit selected</h2><p>Preview and analyze a document, or open a saved audit.</p><div className="action-row"><button className="btn" onClick={() => setSection("new-audit")}>New Audit</button><button className="btn btn-secondary" onClick={() => setSection("reports-history")}>Open saved audit</button></div></section> : <div className="stack">
      <div className="document-bar"><div><h2>{documentName || "Current audit"}</h2><p>{result.total_clauses} clauses · {auditReviewState(result.metadata?.analysis_state, graph)}</p></div><button className="btn btn-secondary" onClick={() => setSection("reports-history")}>Export report</button></div>
      <WorkspaceTabs label="Audit result views" options={RESULT_VIEWS} value={resultView} onChange={setResultView} />
      <div role="tabpanel" id={`panel-${resultView}`} aria-labelledby={`view-${resultView}`}>
        {resultView === "findings" && <FindingGroups result={result} graph={graph} onSelect={goReview} onReferences={() => setResultView("references")} />}
        {resultView === "review" && <ContractReviewWorkspace documentResult={result} rawContractText={result.metadata?.source_text || ""} selectedClauseId={selectedClauseId} onSelectClauseId={setSelectedClauseId} backendUrl={backendUrl} apiKey={apiKey} onNavigateToXai={goExplain} onNavigateToFeedback={() => setSection("reports-history")} />}
        {resultView === "analytics" && <AnalyticsWorkspace documentResult={result} selectedClauseId={selectedClauseId} onSelectClauseId={setSelectedClauseId} onNavigateToReview={() => goReview()} />}
        {resultView === "explanations" && <ExplainabilityWorkspace documentResult={result} selectedClauseId={selectedClauseId} onSelectClauseId={setSelectedClauseId} backendUrl={backendUrl} apiKey={apiKey} onNavigateToReview={() => goReview()} onNavigateToFeedback={() => setSection("reports-history")} onNavigateToUpload={() => setSection("new-audit")} />}
        {resultView === "references" && <ReferenceCheck key={jobId} backendUrl={backendUrl} apiKey={apiKey} jobId={jobId} graph={graph} onGraph={setGraph} />}
      </div></div>)}
    {section === "reports-history" && (!apiKey ? needConnection : <div className="stack"><ReleaseTools key={session} backendUrl={backendUrl} apiKey={apiKey} jobId={jobId} onOpen={openSaved} />
      {result && <section className="card"><h2>Reviewer Feedback</h2><p>Record an observation about the selected clause. Identity and provenance are self-reported; feedback does not retrain the frozen model.</p><form className="stack-form" onSubmit={feedback}>
        <div className="form-grid"><div><label htmlFor="clause-select-fb">Clause</label><select id="clause-select-fb" className="input-field" value={selectedClauseId} onChange={e => setSelectedClauseId(e.target.value)}>{result.scoring_result.clauses.map(c => <option key={c.clause_id} value={c.clause_id}>Clause {c.sequence_idx + 1} · {c.severity.toLowerCase()} severity</option>)}</select></div><div><label htmlFor="feedback-verdict-select">Review decision</label><select id="feedback-verdict-select" className="input-field" value={verdict} onChange={e => setVerdict(e.target.value)}><option value="CONFIRM_ANOMALY">Agree with finding</option><option value="REJECT_ANOMALY">Disagree with finding</option></select></div></div>
        <div className="form-grid"><div><label htmlFor="reviewer-id-input">Reviewer identifier</label><input id="reviewer-id-input" className="input-field" required maxLength={100} value={reviewerId} onChange={e => setReviewerId(e.target.value)} /></div><div><label htmlFor="feedback-provenance-select">Observation type</label><select id="feedback-provenance-select" className="input-field" value={provenance} onChange={e => setProvenance(e.target.value)}><option value="REAL">Human review (credentials unverified)</option><option value="SYNTHETIC_TEST">Synthetic test observation</option></select></div></div>
        <button id="submit-feedback-btn" className="btn" disabled={feedbackBusy || !reviewerId.trim()}>{feedbackBusy ? "Saving…" : "Save feedback"}</button></form>{feedbackStatus && <p role="status">{feedbackStatus}</p>}</section>}</div>)}
    {section === "research-tools" && <div className="stack"><p className="research-notice">Optional research workspaces. Historical and synthetic results are separate from current-document findings.</p><WorkspaceTabs label="Research workspaces" options={RESEARCH_VIEWS} value={researchView} onChange={setResearchView} /><div role="tabpanel" id={`panel-${researchView}`} aria-labelledby={`view-${researchView}`}>
      {researchView === "evaluation" && <ModelEvaluation />}{researchView === "compatibility" && <LearnedCompatibilityWorkspace />}{researchView === "robustness" && <RedTeamWorkspace backendUrl={backendUrl} apiKey={apiKey} activeDocId={result?.doc_id} activeDocClauses={result?.scoring_result.clauses.map(c => ({ clause_id: c.clause_id, sequence_idx: c.sequence_idx, text: result.metadata?.clause_inventory?.find(i => i.clause_id === c.clause_id)?.text || c.text_preview }))} />}
    </div></div>}
  </AppShell></ThemeProvider>;
}
