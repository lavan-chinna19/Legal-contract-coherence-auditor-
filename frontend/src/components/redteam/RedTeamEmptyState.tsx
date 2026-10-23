"use client";

import React from "react";
import { PerturbationType } from "./types";
import { ShieldAlert, ArrowRight, CheckCircle2 } from "lucide-react";

interface RedTeamEmptyStateProps {
  onQuickLaunch: (type: PerturbationType) => void;
}

export function RedTeamEmptyState({ onQuickLaunch }: RedTeamEmptyStateProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center space-y-6 max-w-2xl mx-auto my-6">
      <div className="w-14 h-14 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-blue-500/5">
        <ShieldAlert size={28} />
      </div>

      <div className="space-y-2">
        <h3 className="text-base font-bold text-slate-100">
          Ready to Stress-Test LexAudit Detector Robustness
        </h3>
        <p className="text-xs text-slate-400 max-w-lg mx-auto leading-relaxed">
          The Robustness Laboratory evaluates the existing frozen LexAudit pipeline against controlled, reversible perturbations to quantify sensitivity, false positives, and failure modes.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left pt-2">
        <button
          type="button"
          onClick={() => onQuickLaunch("P1_DISPLACEMENT")}
          className="p-3 bg-slate-950/70 border border-slate-800 hover:border-blue-500/50 rounded-lg text-xs transition-all group cursor-pointer"
        >
          <div className="flex items-center justify-between text-blue-400 font-semibold mb-1">
            <span>P1 Clause Displacement</span>
            <ArrowRight size={13} className="group-hover:translate-x-1 transition-transform" />
          </div>
          <p className="text-[11px] text-slate-400">
            Move Section 2 to contract end to test Channel B discourse transition sensitivity.
          </p>
        </button>

        <button
          type="button"
          onClick={() => onQuickLaunch("P5_BROKEN_REFERENCE")}
          className="p-3 bg-slate-950/70 border border-slate-800 hover:border-red-500/50 rounded-lg text-xs transition-all group cursor-pointer"
        >
          <div className="flex items-center justify-between text-red-400 font-semibold mb-1">
            <span>P5 Broken Cross-Reference</span>
            <ArrowRight size={13} className="group-hover:translate-x-1 transition-transform" />
          </div>
          <p className="text-[11px] text-slate-400">
            Mutate citation to undeclared Section 99 to test spaCy reference checker resolution.
          </p>
        </button>

        <button
          type="button"
          onClick={() => onQuickLaunch("P7_DATE_INVERSION")}
          className="p-3 bg-slate-950/70 border border-slate-800 hover:border-purple-500/50 rounded-lg text-xs transition-all group cursor-pointer"
        >
          <div className="flex items-center justify-between text-purple-400 font-semibold mb-1">
            <span>P7 Chronology Inversion</span>
            <ArrowRight size={13} className="group-hover:translate-x-1 transition-transform" />
          </div>
          <p className="text-[11px] text-slate-400">
            Invert termination date before effective date to test dateparser logic checks.
          </p>
        </button>

        <button
          type="button"
          onClick={() => onQuickLaunch("P9_NEGATIVE_CONTROL")}
          className="p-3 bg-slate-950/70 border border-slate-800 hover:border-emerald-500/50 rounded-lg text-xs transition-all group cursor-pointer"
        >
          <div className="flex items-center justify-between text-emerald-400 font-semibold mb-1">
            <span>P9 Clean Negative Control</span>
            <ArrowRight size={13} className="group-hover:translate-x-1 transition-transform" />
          </div>
          <p className="text-[11px] text-slate-400">
            Execute the unchanged baseline to inspect existing flags and verify prediction stability.
          </p>
        </button>
      </div>

      <div className="pt-2 text-[11px] text-slate-500 font-mono flex items-center justify-center gap-2">
        <CheckCircle2 size={13} className="text-emerald-500" />
        <span>Experiments use temporary document copies</span>
      </div>
    </div>
  );
}
