"use client";

import { useState } from "react";

interface SavedDocument { doc_id: string; name: string; created_at: string; job_id?: string }
interface GraphEvidence {
  source_clause_id: string; reference: string; reason: string;
  target?: { clause_id: string; section_id: string };
}
interface GraphResult { status: string; scope: string; findings: GraphEvidence[]; reviews: GraphEvidence[]; edges: unknown[] }

export function ReleaseTools({ backendUrl, apiKey, jobId, onOpen }: {
  backendUrl: string; apiKey: string; jobId: string;
  onOpen: (jobId: string) => Promise<void>;
}) {
  const [documents, setDocuments] = useState<SavedDocument[]>([]);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [graph, setGraph] = useState<GraphResult | null>(null);
  const [optIn, setOptIn] = useState(false);
  const headers = { "X-API-Key": apiKey.trim() };

  async function checkedFetch(path: string, options?: RequestInit) {
    const response = await fetch(`${backendUrl}${path}`, { ...options, headers: { ...headers, ...options?.headers } });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(typeof data.detail === "string" ? data.detail : `Request failed (${response.status})`);
    }
    return response;
  }

  async function execute(action: () => Promise<void>) {
    setBusy(true); setError(""); setStatus("");
    try { await action(); } catch (e) { setError(e instanceof Error ? e.message : "Request failed"); }
    finally { setBusy(false); }
  }

  function signIn() {
    void execute(async () => {
      await checkedFetch("/v1/session");
      const response = await checkedFetch("/v1/documents");
      setDocuments((await response.json()).documents);
      setStatus("Signed in. Saved documents refreshed. Credentials remain in this page's memory.");
    });
  }

  function download(format: "pdf" | "docx") {
    void execute(async () => {
      const response = await checkedFetch(`/v1/jobs/${jobId}/report/${format}`);
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url; link.download = `LexAudit-${jobId}.${format}`;
      document.body.appendChild(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setStatus(`${format.toUpperCase()} report downloaded.`);
    });
  }

  return <section className="card" aria-label="Sign in, saved documents and reports">
    <h2>Session and reports</h2>
    <p>Enter your API key in Connection, then sign in to reopen saved analyses. Downloads contain sensitive document excerpts.</p>
    <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", margin: "1rem 0" }}>
      <button className="btn btn-secondary" onClick={signIn} disabled={busy || !apiKey.trim()}>Sign in / Refresh saved documents</button>
      {jobId && <>
        <button className="btn" disabled={busy} onClick={() => download("pdf")}>Download PDF report</button>
        <button className="btn" disabled={busy} onClick={() => download("docx")}>Download DOCX report</button>
      </>}
    </div>
    {documents.length > 0 && <details><summary>Saved documents ({documents.length})</summary><ul>
      {documents.map(d => <li key={d.doc_id}>{d.name} — {new Date(d.created_at).toLocaleString()} {d.job_id ?
        <button className="btn btn-secondary" disabled={busy} onClick={() => void execute(async () => { await onOpen(d.job_id!); setGraph(null); })}>Reopen analysis</button> :
        <span>Uploaded; no completed analysis saved</span>}</li>)}
    </ul></details>}
    {jobId && <details><summary>Experimental dependency graph</summary>
      <p>Checks explicit section references and direction. Ambiguous targets require review. This channel does not change model scores.</p>
      <label><input type="checkbox" checked={optIn} onChange={e => setOptIn(e.target.checked)} /> I opt in to experimental dependency checks</label>
      <button className="btn btn-secondary" disabled={!optIn || busy} onClick={() => void execute(async () => {
        const response = await checkedFetch("/v1/experimental/dependencies", { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_id: jobId, experimental: true }) });
        setGraph(await response.json()); setStatus("Dependency evidence saved; subsequent reports include these results.");
      })}>Run dependency checks</button>
      {graph && <div role="status"><h3>{graph.status}</h3><p>{graph.scope}</p>
        <p>{graph.edges.length} explicit references; {graph.findings.length} textual conflicts; {graph.reviews.length} review items.</p>
        {[...graph.findings, ...graph.reviews].map((f, i) => <p key={i}><strong>{f.source_clause_id}</strong>: “{f.reference}” — {f.reason}
          {f.target && ` Target: section ${f.target.section_id}, clause ${f.target.clause_id}.`}</p>)}
      </div>}
    </details>}
    {busy && <p role="status">Working…</p>}
    {status && <p role="status">{status}</p>}
    {error && <p role="alert">{error}</p>}
  </section>;
}
