"use client";

import React from "react";
import { RedTeamCaseResponse } from "./types";
import { CheckCircle2, XCircle, AlertCircle, Info, Clock, Target, Zap } from "lucide-react";

interface DetectionOutcomePanelProps {
  caseResult: RedTeamCaseResponse;
}

export function DetectionOutcomePanel({ caseResult }: DetectionOutcomePanelProps) {
  const status = caseResult.detection_status;

  const getStatusBadge = () => {
    switch (status) {
      case "DETECTED":
        return {
          bg: "bg-emerald-950/40 border-emerald-500/40 text-emerald-300",
          icon: CheckCircle2,
          label: "DETECTED",
          desc: "Frozen pipeline registered the injected perturbation condition.",
        };
      case "NOT_DETECTED":
        return {
          bg: "bg-amber-950/40 border-amber-500/40 text-amber-300",
          icon: XCircle,
          label: "NOT DETECTED",
          desc: "Perturbation applied and oracle-valid; production model remained in CLEAN tier (no new anomaly findings; ΔSB below 0.08 exploratory cutoff).",
        };
      case "NOT_APPLICABLE":
        return {
          bg: "bg-slate-800/60 border-slate-700 text-slate-300",
          icon: Info,
          label: "NOT APPLICABLE (DESCRIPTIVE / CLEAN)",
          desc: caseResult.oracle_result.ground_truth_reason || "Condition outside formal detection scope or clean negative control.",
        };
      case "INVALID_SCENARIO":
        return {
          bg: "bg-red-950/40 border-red-500/40 text-red-300",
          icon: AlertCircle,
          label: "INVALID SCENARIO",
          desc: "Independent Oracle rejected the transformation parameters.",
        };
      default:
        return {
          bg: "bg-slate-800 border-slate-700 text-slate-400",
          icon: Info,
          label: status,
          desc: "Evaluation completed.",
        };
    }
  };

  const badge = getStatusBadge();
  const StatusIcon = badge.icon;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-4">
      {/* Top Banner: Verdict & Attribution */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div id="detection-status-badge" className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono text-xs font-bold ${badge.bg}`}>
            <StatusIcon size={16} />
            <span>{badge.label}</span>
          </div>

          <div className="flex items-center gap-1.5 text-xs">
            <Target size={14} className={caseResult.attribution_valid ? "text-emerald-400" : "text-slate-500"} />
            <span className="text-slate-400">Attribution Validity:</span>
            <span className={`font-mono font-semibold ${caseResult.attribution_valid ? "text-emerald-300" : "text-amber-400"}`}>
              {caseResult.attribution_valid ? "VERIFIED MATCH" : "NON-TARGET / UNATTRIBUTED"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <Clock size={13} className="text-slate-500" />
          <span>Execution Latency: <strong>{caseResult.execution_time_ms} ms</strong></span>
        </div>
      </div>

      {/* Primary Quantitative Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[11px] text-slate-400 block font-sans">Combined Anomaly Delta (ΔS̄)</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-lg font-bold font-mono ${caseResult.delta_mean_combined > 0 ? "text-amber-400" : "text-slate-200"}`}>
              {caseResult.delta_mean_combined > 0 ? `+${caseResult.delta_mean_combined}` : caseResult.delta_mean_combined}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            {caseResult.original_mean_combined} → {caseResult.perturbed_mean_combined}
          </span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[11px] text-slate-400 block font-sans">Max Channel B Shift (ΔSB)</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-lg font-bold font-mono ${caseResult.max_affected_clause_b_delta >= 0.08 ? "text-emerald-400" : "text-slate-200"}`}>
              {caseResult.max_affected_clause_b_delta > 0 ? `+${caseResult.max_affected_clause_b_delta}` : caseResult.max_affected_clause_b_delta}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            Exploratory Cutoff: ≥ 0.0800 (Prod: ≥ 0.50)
          </span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[11px] text-slate-400 block font-sans">New Rule Flags Triggered</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-lg font-bold font-mono ${caseResult.new_rule_flags.length > 0 ? "text-purple-400" : "text-slate-200"}`}>
              {caseResult.new_rule_flags.length}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            Baseline: {caseResult.original_rule_flag_count} flags
          </span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-3">
          <span className="text-[11px] text-slate-400 block font-sans">ML Anomaly Count Delta</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-lg font-bold font-mono ${caseResult.delta_anomaly_count > 0 ? "text-amber-400" : "text-slate-200"}`}>
              {caseResult.delta_anomaly_count > 0 ? `+${caseResult.delta_anomaly_count}` : caseResult.delta_anomaly_count}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            {caseResult.original_anomaly_count} → {caseResult.perturbed_anomaly_count}
          </span>
        </div>
      </div>

      {/* Failure Mode or Descriptive Diagnosis Callout */}
      {(caseResult.failure_category || status === "NOT_DETECTED" || status === "NOT_APPLICABLE") && (
        <div className="bg-slate-950 border border-slate-800/80 rounded-lg p-3 text-xs space-y-1">
          <div className="flex items-center gap-1.5 text-amber-400 font-semibold font-mono text-[11px]">
            <Zap size={14} />
            <span>Diagnosis / Evaluation Classification: {caseResult.failure_category || "RESEARCH_NOTE"}</span>
          </div>
          <p className="text-slate-300 leading-relaxed">
            {caseResult.failure_explanation || badge.desc}
          </p>
        </div>
      )}
    </div>
  );
}
