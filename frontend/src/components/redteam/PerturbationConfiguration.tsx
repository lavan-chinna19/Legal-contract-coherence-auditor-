"use client";

import React from "react";
import { PerturbationType } from "./types";
import { Play, ShieldCheck, Cpu } from "lucide-react";

interface PerturbationConfigurationProps {
  perturbationType: PerturbationType;
  fixtureId: string;
  onSelectFixture: (f: string) => void;
  hasActiveDocument: boolean;
  activeDocId?: string;
  useActiveDocument: boolean;
  onToggleUseActiveDoc: (val: boolean) => void;
  targetClauseId: string;
  onSelectTargetClause: (cid: string) => void;
  availableClauses: Array<{ clause_id: string; sequence_idx: number; text: string }>;
  parameters: Record<string, unknown>;
  onChangeParameters: (params: Record<string, unknown>) => void;
  experimentalOptIn: boolean;
  onToggleOptIn: (opt: boolean) => void;
  onExecute: () => void;
  executing: boolean;
}

export function PerturbationConfiguration({
  perturbationType,
  fixtureId,
  onSelectFixture,
  hasActiveDocument,
  activeDocId,
  useActiveDocument,
  onToggleUseActiveDoc,
  targetClauseId,
  onSelectTargetClause,
  availableClauses,
  parameters,
  onChangeParameters,
  experimentalOptIn,
  onToggleOptIn,
  onExecute,
  executing,
}: PerturbationConfigurationProps) {
  const updateParam = (key: string, val: unknown) => {
    onChangeParameters({ ...parameters, [key]: val });
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Cpu size={16} className="text-blue-400" />
            2. Configure Red-Team Parameters
          </h3>
          <p className="text-xs text-slate-400">
            Define target slots, lexical variants, or contradictory citations.
          </p>
        </div>

        {/* Source Document Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Target Document:</span>
          {hasActiveDocument ? (
            <div className="flex rounded-lg border border-slate-700 bg-slate-950 p-0.5 text-xs">
              <button
                type="button"
                onClick={() => onToggleUseActiveDoc(true)}
                className={`px-2.5 py-1 rounded font-medium transition-all ${
                  useActiveDocument
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Active Upload ({activeDocId?.slice(0, 10)}...)
              </button>
              <button
                type="button"
                onClick={() => onToggleUseActiveDoc(false)}
                className={`px-2.5 py-1 rounded font-medium transition-all ${
                  !useActiveDocument
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Synthetic Fixture
              </button>
            </div>
          ) : (
            <select
              id="redteam-fixture-select"
              value={fixtureId}
              onChange={(e) => onSelectFixture(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded px-2 py-1 font-mono focus:outline-none focus:border-blue-500"
            >
              <option value="SYNTH_DOC_01_MSA">SYNTH_DOC_01_MSA (11 clauses, clean)</option>
              <option value="SYNTH_DOC_02_SLA">SYNTH_DOC_02_SLA (8 clauses, clean)</option>
            </select>
          )}

          {useActiveDocument === false && hasActiveDocument && (
            <select
              id="redteam-fixture-select"
              value={fixtureId}
              onChange={(e) => onSelectFixture(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded px-2 py-1 font-mono focus:outline-none focus:border-blue-500"
            >
              <option value="SYNTH_DOC_01_MSA">SYNTH_DOC_01_MSA (11 clauses)</option>
              <option value="SYNTH_DOC_02_SLA">SYNTH_DOC_02_SLA (8 clauses)</option>
            </select>
          )}
        </div>
      </div>

      {/* Target Clause Selection (if applicable) */}
      {perturbationType !== "P9_NEGATIVE_CONTROL" && (
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300">
            Target Clause to Perturb:
          </label>
          <select
            id="redteam-target-clause-select"
            value={targetClauseId}
            onChange={(e) => onSelectTargetClause(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 font-mono focus:outline-none focus:border-blue-500"
          >
            {availableClauses.map((c) => (
              <option key={c.clause_id} value={c.clause_id}>
                Slot [{c.sequence_idx}] {c.clause_id}: {c.text.slice(0, 80)}...
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Dynamic Type-Specific Parameter Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
        {perturbationType === "P1_DISPLACEMENT" && (
          <>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Source Slot:</label>
              <input
                type="number"
                min={0}
                max={Math.max(availableClauses.length - 1, 0)}
                value={Number(parameters.source_slot ?? 1)}
                onChange={(e) => updateParam("source_slot", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Target Slot (New Index):</label>
              <input
                type="number"
                min={0}
                max={Math.max(availableClauses.length - 1, 0)}
                value={Number(parameters.target_slot ?? (availableClauses.length - 1))}
                onChange={(e) => updateParam("target_slot", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
          </>
        )}

        {perturbationType === "P2_SWAP" && (
          <>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Slot A:</label>
              <input
                type="number"
                min={0}
                max={Math.max(availableClauses.length - 1, 0)}
                value={Number(parameters.slot_a ?? 0)}
                onChange={(e) => updateParam("slot_a", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Slot B:</label>
              <input
                type="number"
                min={0}
                max={Math.max(availableClauses.length - 1, 0)}
                value={Number(parameters.slot_b ?? 1)}
                onChange={(e) => updateParam("slot_b", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
          </>
        )}

        {perturbationType === "P3_EXACT_DUPLICATION" && (
          <>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Source Clause Slot:</label>
              <input
                type="number"
                value={Number(parameters.source_slot ?? 4)}
                onChange={(e) => updateParam("source_slot", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Insertion Slot:</label>
              <input
                type="number"
                value={Number(parameters.insert_slot ?? 8)}
                onChange={(e) => updateParam("insert_slot", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
          </>
        )}

        {perturbationType === "P4_NEAR_DUPLICATION" && (
          <>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Substitution Mode:</label>
              <select
                value={String(parameters.substitution_mode ?? "SYNONYM_REPLACEMENT")}
                onChange={(e) => updateParam("substitution_mode", e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              >
                <option value="SYNONYM_REPLACEMENT">Legal Synonym Replacement</option>
                <option value="COSMETIC_PHRASING">Cosmetic Phrasing Variation</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Insertion Slot:</label>
              <input
                type="number"
                value={Number(parameters.insert_slot ?? 8)}
                onChange={(e) => updateParam("insert_slot", parseInt(e.target.value, 10))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              />
            </div>
          </>
        )}

        {perturbationType === "P5_BROKEN_REFERENCE" && (
          <>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Original Citation to Replace:</label>
              <input
                type="text"
                value={String(parameters.old_target_sec ?? "2")}
                onChange={(e) => updateParam("old_target_sec", e.target.value)}
                placeholder="e.g. 2, 4.1"
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">New Nonexistent Section:</label>
              <input
                type="text"
                value={String(parameters.new_nonexistent_sec ?? "Section 99")}
                onChange={(e) => updateParam("new_nonexistent_sec", e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono"
              />
            </div>
          </>
        )}

        {perturbationType === "P6_MISSING_EXHIBIT" && (
          <div className="col-span-2">
            <label className="text-xs text-slate-400 block mb-1">Nonexistent Exhibit to Cite:</label>
            <input
              type="text"
              value={String(parameters.new_nonexistent_exhibit ?? "Exhibit Z")}
              onChange={(e) => updateParam("new_nonexistent_exhibit", e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono"
            />
          </div>
        )}

        {perturbationType === "P7_DATE_INVERSION" && (
          <>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Inversion Pattern:</label>
              <select
                value={String(parameters.inversion_type ?? "INVERTED_CONTRACT_TERM")}
                onChange={(e) => updateParam("inversion_type", e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
              >
                <option value="INVERTED_CONTRACT_TERM">Termination before Effective Date</option>
                <option value="INVALID_PAYMENT_TIMELINE">Payment Due before Effective Date</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Contradictory Date String:</label>
              <input
                type="text"
                value={String(parameters.new_date_str ?? "December 31, 2020")}
                onChange={(e) => updateParam("new_date_str", e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 font-mono"
              />
            </div>
          </>
        )}

        {perturbationType === "P8_DELETION" && (
          <div className="col-span-2">
            <label className="text-xs text-slate-400 block mb-1">Slot to Delete:</label>
            <input
              type="number"
              min={0}
              max={Math.max(availableClauses.length - 1, 0)}
              value={Number(parameters.target_slot ?? 1)}
              onChange={(e) => updateParam("target_slot", parseInt(e.target.value, 10))}
              className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200"
            />
            <p className="text-[11px] text-amber-400/90 mt-1">
              Note: Strict consequence evaluation is only supported if surviving clauses reference the deleted section.
            </p>
          </div>
        )}

        {perturbationType === "P9_NEGATIVE_CONTROL" && (
          <div className="col-span-2 text-xs text-emerald-400 flex items-center gap-2">
            <ShieldCheck size={16} />
            <span>Clean Negative Control executes untouched baseline document to measure false-positive rate.</span>
          </div>
        )}

        {perturbationType === "P10_COMBINED" && (
          <div className="col-span-2 text-xs text-cyan-400">
            Compound: Evaluates simultaneous structural displacement (Slot 1 to End) + broken internal reference (citing Section 99).
          </div>
        )}
      </div>

      {/* Opt-in Security Guard & Execution Action */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            id="redteam-opt-in-checkbox"
            checked={experimentalOptIn}
            onChange={(e) => onToggleOptIn(e.target.checked)}
            className="w-4 h-4 rounded border-slate-700 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900 bg-slate-950"
          />
          <span className="text-xs text-slate-300">
            I explicitly authorize experimental red-team perturbation evaluation (Contract §7/§20 Opt-in)
          </span>
        </label>

        <button
          type="button"
          id="btn-run-redteam-experiment"
          disabled={!experimentalOptIn || executing}
          onClick={onExecute}
          className="rt-btn-primary"
        >
          {executing ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Running Frozen Pipeline...</span>
            </>
          ) : (
            <>
              <Play size={14} className="fill-current" />
              <span>Execute Red-Team Test</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
