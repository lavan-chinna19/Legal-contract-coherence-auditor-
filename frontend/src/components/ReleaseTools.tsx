"use client";
import { useEffect, useRef, useState } from "react";
import { requestError } from "../lib/workflow";
interface SavedDocument { doc_id: string; name: string; created_at: string; job_id?: string }
export function ReleaseTools({ backendUrl, apiKey, jobId, onOpen }: {
  backendUrl: string; apiKey: string; jobId: string; onOpen: (jobId: string, name: string) => Promise<void>;
}) {
  const [documents, setDocuments] = useState<SavedDocument[]>([]), [status, setStatus] = useState(""), [error, setError] = useState("");
  const [busy, setBusy] = useState(false), [loaded, setLoaded] = useState(false);
  const controller = useRef<AbortController | null>(null);
  useEffect(() => {
    const abort = new AbortController(); controller.current = abort;
    fetch(`${backendUrl}/v1/documents`, { headers: { "X-API-Key": apiKey }, signal: abort.signal, cache: "no-store", redirect: "error" })
      .then(async r => { if (!r.ok) throw new Error(await requestError(r)); return r.json(); })
      .then(data => { if (!abort.signal.aborted) { setDocuments(data.documents); setLoaded(true); } })
      .catch(e => { if (!abort.signal.aborted) setError(e instanceof Error ? e.message : "History unavailable."); });
    return () => abort.abort();
  }, [backendUrl, apiKey, jobId]);
  async function execute(action: () => Promise<void>) {
    setBusy(true); setError(""); setStatus("");
    try { await action(); } catch (e) { if (!controller.current?.signal.aborted) setError(e instanceof Error ? e.message : "Request failed."); }
    finally { setBusy(false); }
  }
  async function download(format: "pdf" | "docx") {
    const response = await fetch(`${backendUrl}/v1/jobs/${jobId}/report/${format}`, { headers: { "X-API-Key": apiKey }, signal: controller.current?.signal, redirect: "error", cache: "no-store" });
    if (!response.ok) throw new Error(await requestError(response));
    const blob = await response.blob(); if (controller.current?.signal.aborted) return;
    const url = URL.createObjectURL(blob), link = document.createElement("a"); link.href = url; link.download = `LexAudit-${jobId}.${format}`;
    document.body.appendChild(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    setStatus(`${format.toUpperCase()} report downloaded.`);
  }
  return <div className="stack"><section className="card"><h2>Export current audit</h2><p>Reports include saved findings and reference evidence. Exports contain sensitive excerpts.</p>
    <div className="action-row"><button className="btn" disabled={busy || !jobId} onClick={() => void execute(() => download("pdf"))}>Download PDF</button><button className="btn btn-secondary" disabled={busy || !jobId} onClick={() => void execute(() => download("docx"))}>Download DOCX</button></div>
    {!jobId && <p>Open or complete an audit to export a report.</p>}</section>
    <section className="card"><div className="section-row"><h2>Saved audits</h2><button className="btn btn-secondary" disabled={busy} onClick={() => void execute(async () => {
      const r = await fetch(`${backendUrl}/v1/documents`, { headers: { "X-API-Key": apiKey }, signal: controller.current?.signal, redirect: "error", cache: "no-store" });
      if (!r.ok) throw new Error(await requestError(r)); setDocuments((await r.json()).documents); setLoaded(true); setStatus("History refreshed.");
    })}>Refresh history</button></div>
    {!loaded && !error && <p role="status">Loading saved audits…</p>}{loaded && documents.length === 0 && <p>No saved audits for this identity. Start a new audit to create one.</p>}
    <ul className="saved-audits">{documents.map(d => <li key={d.doc_id}><div><strong>{d.name}</strong><p>{new Date(d.created_at).toLocaleString()}</p></div>{d.job_id ? <button className="btn btn-secondary" disabled={busy} onClick={() => void execute(() => onOpen(d.job_id!, d.name))}>Open audit</button> : <span className="quiet-label">Analysis not completed</span>}</li>)}</ul></section>
    {busy && <p role="status">Working…</p>}{status && <p role="status">{status}</p>}{error && <p role="alert" className="inline-error">{error}</p>}</div>;
}
