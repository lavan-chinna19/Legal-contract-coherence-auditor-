"use client";

import React from "react";
import { RedTeamCaseResponse } from "./types";
import { CheckCircle2, XCircle, Search, ShieldCheck } from "lucide-react";

interface ScenarioEvidenceInspectorProps {
  caseResult: RedTeamCaseResponse;
}

export function ScenarioEvidenceInspector({ caseResult }: ScenarioEvidenceInspectorProps) {
  const oracle = caseResult.oracle_result;
  const conditions = oracle.conditions || [];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Search size={16} className="text-cyan-400" />
          <h4 className="text-xs font-bold text-slate-100 tracking-wide">
            6. Independent Ground-Truth Oracle Evidence &amp; Invariants
          </h4>
        </div>
        <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded flex items-center gap-1.5">
          <ShieldCheck size={13} />
          Non-Circular Ground Truth
        </span>
      </div>

      <div className="text-xs text-slate-300 space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Oracle Evaluated Condition:</span>
          <span className="font-mono font-bold text-cyan-300 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40">
            {oracle.oracle_condition}
          </span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400">Strict Evaluation Eligible:</span>
          <span className={`font-mono font-semibold ${oracle.eligible_for_strict_evaluation ? "text-emerald-400" : "text-amber-400"}`}>
            {oracle.eligible_for_strict_evaluation ? "ELIGIBLE" : "DESCRIPTIVE / EXPLORATORY"}
          </span>
        </div>

        <p className="text-[11px] text-slate-400 italic">
          {oracle.ground_truth_reason}
        </p>
      </div>

      {/* Conditions Table */}
      <div className="bg-slate-950/70 border border-slate-800 rounded-lg overflow-hidden">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[10px] font-mono text-slate-400 bg-slate-900/60">
              <th className="py-2 px-3">Condition Name</th>
              <th className="py-2 px-3">Property</th>
              <th className="py-2 px-3">Expected Value</th>
              <th className="py-2 px-3">Observed Value</th>
              <th className="py-2 px-3 text-right">Oracle Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
            {conditions.map((cond, i) => (
              <tr key={cond.condition_name || i} className={cond.is_satisfied ? "text-slate-300" : "text-red-300 bg-red-950/20"}>
                <td className="py-2 px-3 font-sans font-medium text-slate-200">
                  {cond.condition_name}
                </td>
                <td className="py-2 px-3 text-slate-400">{cond.target_property}</td>
                <td className="py-2 px-3 text-slate-400 truncate max-w-[120px]">{String(cond.expected_value)}</td>
                <td className="py-2 px-3 text-slate-300 truncate max-w-[120px]">{String(cond.observed_value)}</td>
                <td className="py-2 px-3 text-right">
                  {cond.is_satisfied ? (
                    <span className="inline-flex items-center gap-1 text-emerald-400 font-bold">
                      <CheckCircle2 size={13} />
                      PASS
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-red-400 font-bold">
                      <XCircle size={13} />
                      FAIL
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
