"use client";
import { useEffect, useRef, useState } from "react";
import { requestError } from "../../lib/workflow";
import type { DependencyGraphResult } from "../review/types";
export function ReferenceCheck({ backendUrl, apiKey, jobId, graph, onGraph }: {
  backendUrl: string; apiKey: string; jobId: string; graph: DependencyGraphResult | null; onGraph: (graph: DependencyGraphResult) => void;
}) {
  const [optIn, setOptIn] = useState(false), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);
  useEffect(() => { const abort = new AbortController(); controller.current = abort; return () => abort.abort(); }, []);
  async function run() {
    setBusy(true); setError("");
    try {
      const response = await fetch(`${backendUrl}/v1/experimental/dependencies`, { method: "POST", headers: { "X-API-Key": apiKey, "Content-Type": "application/json" }, body: JSON.stringify({ job_id: jobId, experimental: true }), signal: controller.current?.signal, redirect: "error" });
      if (!response.ok) throw new Error(await requestError(response));
      const data = await response.json(); if (!controller.current?.signal.aborted) onGraph(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Reference check failed."); }
    finally { setBusy(false); }
  }
  return <section className="card" aria-label="Reference Consistency Check (Experimental)"><h2>Reference Consistency Check <span className="quiet-label">Experimental</span></h2>
    <p>Checks supported explicit section references and direction. Uncertain targets require review. This separate channel does not change model scores or determine legal effect.</p>
    <label className="consent-row"><input id="reference-opt-in" type="checkbox" checked={optIn} onChange={e => setOptIn(e.target.checked)} />I opt in to experimental reference checks.</label>
    <button id="run-reference-check" className="btn btn-secondary" disabled={!optIn || busy} onClick={() => void run()}>{busy ? "Checking references…" : "Check references"}</button>
    {error && <p className="inline-error" role="alert">{error}</p>}{graph && <div className="reference-evidence" role="status"><p>{graph.findings.length} supported textual conflicts · {graph.reviews.length} unresolved references. Evidence is saved with this audit and included in subsequent exports.</p>
      {[...graph.findings, ...graph.reviews].map((item, i) => <details key={i}><summary>{item.reference || "Reference requires review"}</summary><p>{item.reason}</p><p>Source clause: {item.source_clause_id}{item.target && ` · Target section ${item.target.section_id}, clause ${item.target.clause_id}`}</p></details>)}
      <details><summary>Scope and interpretation</summary><p>{graph.scope}</p><p>No findings means no supported textual conflict was detected, not proof of legal correctness.</p></details>
    </div>}</section>;
}
