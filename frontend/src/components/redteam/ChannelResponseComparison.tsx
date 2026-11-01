"use client";

import React from "react";
import { RedTeamCaseResponse } from "./types";
import { Split } from "lucide-react";

interface ChannelResponseComparisonProps {
  caseResult: RedTeamCaseResponse;
}

export function ChannelResponseComparison({ caseResult }: ChannelResponseComparisonProps) {
  const abl = {
    chA: caseResult.channel_a_only_delta,
    chB: caseResult.channel_b_only_delta,
    combined: caseResult.dual_channel_combined_delta,
    rules: caseResult.new_rule_flags.length,
    integrated: caseResult.new_rule_flags.length + Math.max(caseResult.delta_anomaly_count, 0),
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Split size={16} className="text-blue-400" />
          <h4 className="text-xs font-bold text-slate-100 tracking-wide">
            4. Dual-Channel Behavioral Response &amp; Ablation Decomposition
          </h4>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          Configured frozen ensemble; measured channel deltas below
        </span>
      </div>

      {/* Two Column Channel Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Channel A: Semantic OOD */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-blue-300">
              Channel A: Semantic Out-of-Distribution (LEDGAR Centroids)
            </span>
            <span className="text-[10px] font-mono bg-blue-950/50 text-blue-400 border border-blue-800/40 px-1.5 py-0.5 rounded">
              Position-Invariant
            </span>
          </div>

          <div className="flex items-baseline justify-between pt-1">
            <span className="text-xs text-slate-400">Mean Score Delta (ΔSA):</span>
            <span className="font-mono text-sm font-bold text-slate-200">
              {caseResult.mean_channel_a_delta > 0 ? `+${caseResult.mean_channel_a_delta}` : caseResult.mean_channel_a_delta}
            </span>
          </div>

          <p className="text-[11px] text-slate-400 leading-relaxed border-t border-slate-900 pt-2">
             Channel A embeds clauses individually against LEDGAR topic centroids. Structural displacement (P1) and swaps (P2) yield ΔSA ≈ 0.0 because semantic content is unchanged.
          </p>
        </div>

        {/* Channel B: Discourse Transition */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-indigo-300">
              Channel B: Discourse Transition Coherence (Legal-BERT)
            </span>
            <span className="text-[10px] font-mono bg-indigo-950/50 text-indigo-400 border border-indigo-800/40 px-1.5 py-0.5 rounded">
              Transition-Sensitive
            </span>
          </div>

          <div className="flex items-baseline justify-between pt-1">
            <span className="text-xs text-slate-400">Mean Score Delta (ΔSB):</span>
            <span className="font-mono text-sm font-bold text-slate-200">
              {caseResult.mean_channel_b_delta > 0 ? `+${caseResult.mean_channel_b_delta}` : caseResult.mean_channel_b_delta}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <span className="text-xs text-slate-400">Max Boundary Shift:</span>
            <span className={`font-mono text-sm font-bold ${caseResult.max_affected_clause_b_delta >= 0.08 ? "text-emerald-400" : "text-amber-400"}`}>
              {caseResult.max_affected_clause_b_delta > 0 ? `+${caseResult.max_affected_clause_b_delta}` : caseResult.max_affected_clause_b_delta}
            </span>
          </div>

          <p className="text-[11px] text-slate-400 leading-relaxed border-t border-slate-900 pt-2">
            Channel B scores adjacent clause pairs. Changed boundaries may change its outputs; a displacement need not produce a detectable score increase.
          </p>
        </div>
      </div>

      {/* Ablation Table */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-lg overflow-hidden">
        <div className="px-3 py-2 bg-slate-900/60 border-b border-slate-800 text-[11px] font-semibold text-slate-300 flex items-center justify-between">
          <span>Read-Only Scoring Ablation Decomposition</span>
          <span className="text-[10px] text-slate-500 font-mono">Independent Channel Contributions</span>
        </div>
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[10px] font-mono text-slate-400 bg-slate-950/40">
              <th className="py-2 px-3">Evaluation Subsystem</th>
              <th className="py-2 px-3">Primary Response Metric</th>
              <th className="py-2 px-3 text-right">Measured Delta / Finding</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-xs text-slate-300">
            <tr>
              <td className="py-2 px-3 font-sans font-medium text-slate-300">1. Channel A Only</td>
              <td className="py-2 px-3 text-slate-400">Semantic OOD Shift</td>
              <td className="py-2 px-3 text-right">{abl.chA > 0 ? `+${abl.chA}` : abl.chA}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-medium text-slate-300">2. Channel B Only</td>
              <td className="py-2 px-3 text-slate-400">Discourse Transition Shift</td>
              <td className="py-2 px-3 text-right">{abl.chB > 0 ? `+${abl.chB}` : abl.chB}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-medium text-slate-300">3. Dual-Channel Ensemble</td>
              <td className="py-2 px-3 text-slate-400">Combined Anomaly Delta (ΔS̄)</td>
              <td className="py-2 px-3 text-right">{abl.combined > 0 ? `+${abl.combined}` : abl.combined}</td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans font-medium text-slate-300">4. Rule Checkers Only</td>
              <td className="py-2 px-3 text-slate-400">New Rule Violations</td>
              <td className="py-2 px-3 text-right">{abl.rules} flag(s)</td>
            </tr>
            <tr className="bg-blue-950/20 font-bold text-blue-200">
              <td className="py-2 px-3 font-sans">5. Full Integrated Pipeline</td>
              <td className="py-2 px-3 text-blue-300/80">Total Identified Disturbances</td>
              <td className="py-2 px-3 text-right text-blue-300">{abl.integrated} finding(s)</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
