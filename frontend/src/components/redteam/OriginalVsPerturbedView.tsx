"use client";

import React, { useState } from "react";
import { RedTeamCaseResponse } from "./types";
import { ArrowRight, FileDiff } from "lucide-react";

interface OriginalVsPerturbedViewProps {
  caseResult: RedTeamCaseResponse;
}

export function OriginalVsPerturbedView({ caseResult }: OriginalVsPerturbedViewProps) {
  const [activeViewMode, setActiveViewMode] = useState<"side_by_side" | "perturbed_only">("side_by_side");

  const origClauses = caseResult.original_clauses_preview || [];
  const pertClauses = caseResult.perturbed_clauses_preview || [];
  const affectedIds = new Set(caseResult.affected_clause_ids || []);

  const checksumMatch = caseResult.original_checksum === caseResult.perturbed_checksum;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden space-y-0">
      {/* Header with Checksums and View Mode Toggle */}
      <div className="p-3.5 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <FileDiff size={17} className="text-blue-400" />
          <h4 className="text-xs font-bold text-slate-100 tracking-wide">
            3. Original vs. Ephemeral Perturbed Representation
          </h4>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-slate-800 bg-slate-900 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => setActiveViewMode("side_by_side")}
              className={`px-2.5 py-0.5 rounded font-medium transition-all ${
                activeViewMode === "side_by_side"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Side-by-Side Diff
            </button>
            <button
              type="button"
              onClick={() => setActiveViewMode("perturbed_only")}
              className={`px-2.5 py-0.5 rounded font-medium transition-all ${
                activeViewMode === "perturbed_only"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Perturbed Only ({pertClauses.length})
            </button>
          </div>
        </div>
      </div>

      {/* Checksum & Immutability Ledger Banner */}
      <div className="px-4 py-2 bg-slate-950/70 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono">
        <div className="flex items-center gap-3">
          <span className="text-slate-400">Orig SHA-256:</span>
          <span className="text-slate-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
            {caseResult.original_checksum.slice(0, 16)}...
          </span>
          <ArrowRight size={12} className="text-slate-500" />
          <span className="text-slate-400">Perturbed:</span>
          <span className={`px-2 py-0.5 rounded border ${checksumMatch ? "text-emerald-400 bg-emerald-950/30 border-emerald-800" : "text-amber-400 bg-amber-950/30 border-amber-800"}`}>
            {caseResult.perturbed_checksum.slice(0, 16)}...
          </span>
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-sans text-[11px]">Original Contract State: <strong>100% Immutable</strong></span>
        </div>
      </div>

      {/* Document Diff Viewer */}
      <div className="p-4">
        {activeViewMode === "side_by_side" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Left: Original Sequence */}
            <div className="space-y-2">
              <div className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase flex items-center justify-between">
                <span>Original Untouched Sequence ({origClauses.length} clauses)</span>
                <span className="text-[10px] text-slate-500 font-mono">Baseline</span>
              </div>
              <div className="space-y-1.5 max-h-[380px] overflow-y-auto pr-1">
                {origClauses.map((c) => {
                  const isAffected = affectedIds.has(c.clause_id);
                  return (
                    <div
                      key={`orig-${c.clause_id}-${c.sequence_idx}`}
                      className={`p-2.5 rounded-lg border text-xs leading-relaxed transition-all ${
                        isAffected
                          ? "bg-blue-950/20 border-blue-500/40 text-blue-200"
                          : "bg-slate-950/50 border-slate-800/80 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-[10px] text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                          Slot [{c.sequence_idx}]
                        </span>
                        <span className="font-mono text-[10px] text-slate-500 truncate max-w-[140px]">
                          {c.clause_id}
                        </span>
                      </div>
                      <p className="line-clamp-3">{c.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Perturbed Ephemeral Sequence */}
            <div className="space-y-2">
              <div className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase flex items-center justify-between">
                <span>In-Memory Perturbed Sequence ({pertClauses.length} clauses)</span>
                <span className="text-[10px] text-amber-400 font-mono">Experimental Copy</span>
              </div>
              <div className="space-y-1.5 max-h-[380px] overflow-y-auto pr-1">
                {pertClauses.map((c) => {
                  const isAffected = affectedIds.has(c.clause_id) || c.clause_id.includes("dup") || c.clause_id.includes("variant");
                  return (
                    <div
                      key={`pert-${c.clause_id}-${c.sequence_idx}`}
                      className={`p-2.5 rounded-lg border text-xs leading-relaxed transition-all ${
                        isAffected
                          ? "bg-amber-950/25 border-amber-500/50 text-amber-200 shadow-sm shadow-amber-500/10"
                          : "bg-slate-950/50 border-slate-800/80 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-[10px] text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                            Slot [{c.sequence_idx}]
                          </span>
                          {isAffected && (
                            <span className="font-mono text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/40 px-1.5 py-0.5 rounded font-bold">
                              PERTURBED TARGET
                            </span>
                          )}
                        </div>
                        <span className="font-mono text-[10px] text-slate-500 truncate max-w-[140px]">
                          {c.clause_id}
                        </span>
                      </div>
                      <p className="line-clamp-3">{c.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* Perturbed Only Single Column View */
          <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
            {pertClauses.map((c) => {
              const isAffected = affectedIds.has(c.clause_id) || c.clause_id.includes("dup");
              return (
                <div
                  key={`pert-single-${c.clause_id}-${c.sequence_idx}`}
                  className={`p-3 rounded-lg border text-xs leading-relaxed ${
                    isAffected
                      ? "bg-amber-950/30 border-amber-500/50 text-amber-100"
                      : "bg-slate-950/60 border-slate-800 text-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      Slot [{c.sequence_idx}] — {c.clause_id}
                    </span>
                    {isAffected && (
                      <span className="font-mono text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded font-bold">
                        AFFECTED EXPERIMENTAL TARGET
                      </span>
                    )}
                  </div>
                  <p>{c.text}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
