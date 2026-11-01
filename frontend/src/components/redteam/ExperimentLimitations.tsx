"use client";

import React from "react";
import { Scale } from "lucide-react";

export function ExperimentLimitations() {
  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
        <Scale size={16} className="text-amber-400" />
        <span>7. Scientific Methodology, Confidentiality &amp; Research Limitations</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="p-3 rounded-lg border border-slate-800/80 bg-slate-900/50 space-y-1">
          <span className="font-semibold text-slate-200 block"> Synthetic vs. Real Drafting</span>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            Injected perturbations (e.g. artificial clause swaps, displaced sections) represent controlled algorithmic disturbances. Detection of a synthetic disturbance does not equate to a finding of legal invalidity.
          </p>
        </div>

        <div className="p-3 rounded-lg border border-slate-800/80 bg-slate-900/50 space-y-1">
          <span className="font-semibold text-slate-200 block"> Ephemeral Zero-Mutation</span>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            All transformations operate strictly on copy-on-write transient memory. Your original contract text, database records, and active audit findings remain strictly untouched and immutable.
          </p>
        </div>

        <div className="p-3 rounded-lg border border-slate-800/80 bg-slate-900/50 space-y-1">
          <span className="font-semibold text-slate-200 block"> Honest Failure Reporting</span>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            LexAudit does not possess a dedicated duplicate clause detector or universal completeness oracle. Undetected perturbations are reported transparently as model limitations, not masked as artificial successes.
          </p>
        </div>
      </div>
    </div>
  );
}
