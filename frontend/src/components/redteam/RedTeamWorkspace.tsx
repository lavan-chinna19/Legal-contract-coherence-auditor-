"use client";

import React, { useState, useMemo } from "react";
import { PerturbationType, RedTeamCaseResponse } from "./types";
import { PerturbationSelector } from "./PerturbationSelector";
import { PerturbationConfiguration } from "./PerturbationConfiguration";
import { OriginalVsPerturbedView } from "./OriginalVsPerturbedView";
import { DetectionOutcomePanel } from "./DetectionOutcomePanel";
import { ChannelResponseComparison } from "./ChannelResponseComparison";
import { RuleDetectionPanel } from "./RuleDetectionPanel";
import { ScenarioEvidenceInspector } from "./ScenarioEvidenceInspector";
import { ExperimentLimitations } from "./ExperimentLimitations";
import { RedTeamEmptyState } from "./RedTeamEmptyState";
import { FlaskConical, RefreshCw, AlertTriangle } from "lucide-react";

// Synthetic Fixtures Definition for client-side selection
const SYNTHETIC_MSA_CLAUSES = [
  { clause_id: "SYNTH_DOC_01_MSA_c00", sequence_idx: 0, text: "Section 1. Preamble and Parties. This Master Services Agreement is entered into as of January 1, 2025 by and between Client Inc. and Provider LLC.", label: "Preamble" },
  { clause_id: "SYNTH_DOC_01_MSA_c01", sequence_idx: 1, text: "Section 2. Scope of Services. Provider agrees to provide software development and consulting services as described in Exhibit A attached hereto.", label: "Services" },
  { clause_id: "SYNTH_DOC_01_MSA_c02", sequence_idx: 2, text: "Section 3. Payment Terms. Invoices shall be payable within thirty (30) days of receipt. Payment due date shall be on or after the Effective Date.", label: "Payment" },
  { clause_id: "SYNTH_DOC_01_MSA_c03", sequence_idx: 3, text: "Section 4. Intellectual Property. All work product developed pursuant to Section 2 shall be deemed work made for hire owned by Client.", label: "Intellectual Property" },
  { clause_id: "SYNTH_DOC_01_MSA_c04", sequence_idx: 4, text: "Section 5. Confidentiality. Each party agrees to maintain in strict confidence all proprietary information disclosed under this Agreement.", label: "Confidentiality" },
  { clause_id: "SYNTH_DOC_01_MSA_c05", sequence_idx: 5, text: "Section 6. Term and Termination. The effective date of this Agreement is January 1, 2025 and the termination date shall be December 31, 2025.", label: "Term" },
  { clause_id: "SYNTH_DOC_01_MSA_c06", sequence_idx: 6, text: "Section 7. Indemnification. Provider shall defend and indemnify Client against any third-party claims arising from a breach of Section 5.", label: "Indemnification" },
  { clause_id: "SYNTH_DOC_01_MSA_c07", sequence_idx: 7, text: "Section 8. Limitation of Liability. Neither party shall be liable for indirect or consequential damages arising under this Agreement.", label: "Liability" },
  { clause_id: "SYNTH_DOC_01_MSA_c08", sequence_idx: 8, text: "Section 9. Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.", label: "Governing Law" },
  { clause_id: "SYNTH_DOC_01_MSA_c09", sequence_idx: 9, text: "Section 10. Miscellaneous. This Agreement, including Exhibit A, constitutes the entire understanding between the parties.", label: "Miscellaneous" },
  { clause_id: "SYNTH_DOC_01_MSA_c10", sequence_idx: 10, text: "Exhibit A. Statement of Work. Scope details, technical deliverables, and milestone specifications.", label: "Exhibit" }
];

const SYNTHETIC_SLA_CLAUSES = [
  { clause_id: "SYNTH_DOC_02_SLA_c00", sequence_idx: 0, text: "Section 1. Grant of License. Licensor grants Licensee a non-exclusive, non-transferable license to use the Software.", label: "License Grant" },
  { clause_id: "SYNTH_DOC_02_SLA_c01", sequence_idx: 1, text: "Section 2. Permitted Users. Use of the Software is limited to authorized employees pursuant to Section 1.", label: "Users" },
  { clause_id: "SYNTH_DOC_02_SLA_c02", sequence_idx: 2, text: "Section 3. Fees and Taxes. Licensee shall pay the annual subscription fees set forth in Section 4.", label: "Fees" },
  { clause_id: "SYNTH_DOC_02_SLA_c03", sequence_idx: 3, text: "Section 4. Schedule of Fees. Annual subscription fee shall be $50,000 payable upon execution.", label: "Fee Schedule" },
  { clause_id: "SYNTH_DOC_02_SLA_c04", sequence_idx: 4, text: "Section 5. Warranty Disclaimer. Licensor disclaims all implied warranties of merchantability and fitness for a particular purpose.", label: "Warranty" },
  { clause_id: "SYNTH_DOC_02_SLA_c05", sequence_idx: 5, text: "Section 6. Audit Rights. Licensor may audit Licensee's software deployment once annually upon reasonable notice.", label: "Audit" },
  { clause_id: "SYNTH_DOC_02_SLA_c06", sequence_idx: 6, text: "Section 7. Term. The initial term begins on March 1, 2025 and expires on February 28, 2026.", label: "Term" },
  { clause_id: "SYNTH_DOC_02_SLA_c07", sequence_idx: 7, text: "Section 8. Dispute Resolution. Any dispute under this Agreement shall be resolved through binding arbitration.", label: "Dispute" }
];

interface RedTeamWorkspaceProps {
  backendUrl?: string;
  apiKey?: string;
  activeDocId?: string;
  activeDocClauses?: Array<{ clause_id: string; sequence_idx: number; text: string }>;
}

export function RedTeamWorkspace({
  backendUrl = "http://localhost:8000",
  apiKey = "",
  activeDocId,
  activeDocClauses = [],
}: RedTeamWorkspaceProps) {
  const [selectedType, setSelectedType] = useState<PerturbationType>("P1_DISPLACEMENT");
  const [fixtureId, setFixtureId] = useState<string>("SYNTH_DOC_01_MSA");
  const [useActiveDocument, setUseActiveDocument] = useState<boolean>(false);
  const [targetClauseId, setTargetClauseId] = useState<string>("");
  const [parameters, setParameters] = useState<Record<string, unknown>>({
    source_slot: 1,
    target_slot: 10,
  });
  const [experimentalOptIn, setExperimentalOptIn] = useState<boolean>(false);
  const [executing, setExecuting] = useState<boolean>(false);
  const [caseResult, setCaseResult] = useState<RedTeamCaseResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Available clauses in chosen target
  const availableClauses = useMemo(() => {
    if (useActiveDocument && activeDocClauses.length > 0) {
      return activeDocClauses;
    }
    return fixtureId === "SYNTH_DOC_02_SLA" ? SYNTHETIC_SLA_CLAUSES : SYNTHETIC_MSA_CLAUSES;
  }, [useActiveDocument, activeDocClauses, fixtureId]);

  // Derive effective target clause ID
  const effectiveTargetClauseId = useMemo(() => {
    if (targetClauseId && availableClauses.some((c) => c.clause_id === targetClauseId)) {
      return targetClauseId;
    }
    return availableClauses[0]?.clause_id || "";
  }, [availableClauses, targetClauseId]);

  // Reset parameters when perturbation type changes
  const handleSelectType = (type: PerturbationType) => {
    setSelectedType(type);
    if (type === "P1_DISPLACEMENT") {
      setParameters({ source_slot: 1, target_slot: Math.max(availableClauses.length - 1, 0) });
      if (availableClauses.length > 1) setTargetClauseId(availableClauses[1].clause_id);
    } else if (type === "P2_SWAP") {
      setParameters({ slot_a: 0, slot_b: 1 });
    } else if (type === "P3_EXACT_DUPLICATION") {
      setParameters({ source_slot: 4, insert_slot: 8 });
      if (availableClauses.length > 4) setTargetClauseId(availableClauses[4].clause_id);
    } else if (type === "P4_NEAR_DUPLICATION") {
      setParameters({ source_slot: 4, insert_slot: 8, substitution_mode: "SYNONYM_REPLACEMENT" });
      if (availableClauses.length > 4) setTargetClauseId(availableClauses[4].clause_id);
    } else if (type === "P5_BROKEN_REFERENCE") {
      setParameters({ old_target_sec: "2", new_nonexistent_sec: "Section 99" });
      // In MSA, Section 4 cites Section 2
      const c = availableClauses.find((cl) => cl.text.includes("Section 4") || cl.sequence_idx === 3);
      if (c) setTargetClauseId(c.clause_id);
    } else if (type === "P6_MISSING_EXHIBIT") {
      setParameters({ new_nonexistent_exhibit: "Exhibit Z" });
      const c = availableClauses.find((cl) => cl.text.includes("Exhibit A"));
      if (c) setTargetClauseId(c.clause_id);
    } else if (type === "P7_DATE_INVERSION") {
      setParameters({ inversion_type: "INVERTED_CONTRACT_TERM", new_date_str: "December 31, 2020" });
      const c = availableClauses.find((cl) => cl.text.includes("effective date") || cl.text.includes("termination date"));
      if (c) setTargetClauseId(c.clause_id);
    } else if (type === "P8_DELETION") {
      setParameters({ target_slot: 1 });
      if (availableClauses.length > 1) setTargetClauseId(availableClauses[1].clause_id);
    } else if (type === "P9_NEGATIVE_CONTROL") {
      setParameters({});
    } else if (type === "P10_COMBINED") {
      setParameters({
        steps: [
          { type: "P1_DISPLACEMENT", source_slot: 1, target_slot: Math.max(availableClauses.length - 1, 0) },
          { type: "P5_BROKEN_REFERENCE", target_clause_id: availableClauses[availableClauses.length > 6 ? 6 : 0].clause_id, old_target_sec: "5", new_sec: "Section 99" },
        ],
      });
    }
  };

  const handleExecute = async () => {
    if (!experimentalOptIn) {
      alert("Opt in before running a research experiment.");
      return;
    }

    try {
      setExecuting(true);
      setErrorMessage(null);

      const payload: Record<string, unknown> = {
        perturbation_type: selectedType,
        parameters: parameters,
        target_clause_ids: selectedType === "P9_NEGATIVE_CONTROL" ? [] : [effectiveTargetClauseId],
        experimental: true,
      };

      if (useActiveDocument && activeDocId) {
        payload.doc_id = activeDocId;
      } else {
        payload.fixture_id = fixtureId;
      }

      const res = await fetch(`${backendUrl}/v1/experimental/redteam`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey.trim(),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned ${res.status}`);
      }

      const data: RedTeamCaseResponse = await res.json();
      setCaseResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Execution failed";
      setErrorMessage(msg);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="rt-workspace" id="robustness-lab-workspace">
      {/* Workspace Header */}
      <div className="rt-header-banner">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <FlaskConical size={18} />
            </div>
            <h2 className="text-base font-bold text-slate-100">
              Robustness Testing (Research)
            </h2>
            <span className="text-[10px] font-mono bg-blue-950/60 text-blue-300 border border-blue-800/40 px-2 py-0.5 rounded font-bold">
              Research
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Generates controlled, reversible perturbations to measure existing frozen detector sensitivity, false-positive resistance, and structural boundary shifts without mutating original documents.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {caseResult && (
            <button
              type="button"
              onClick={() => setCaseResult(null)}
              className="text-xs text-slate-400 hover:text-slate-200 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 flex items-center gap-1.5 transition-all"
            >
              <RefreshCw size={13} />
              <span>Reset Results</span>
            </button>
          )}
        </div>
      </div>

      {/* Error Callout */}
      {errorMessage && (
        <div className="p-3 bg-red-950/40 border border-red-500/50 rounded-xl text-xs text-red-200 flex items-center gap-2">
          <AlertTriangle size={16} className="text-red-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* 1. Taxonomy Category Selector */}
      <PerturbationSelector
        selectedType={selectedType}
        onSelectType={handleSelectType}
        disabled={executing}
      />

      {/* 2. Perturbation Configuration */}
      <PerturbationConfiguration
        perturbationType={selectedType}
        fixtureId={fixtureId}
        onSelectFixture={setFixtureId}
        hasActiveDocument={Boolean(activeDocId && activeDocClauses.length > 0)}
        activeDocId={activeDocId}
        useActiveDocument={useActiveDocument}
        onToggleUseActiveDoc={setUseActiveDocument}
        targetClauseId={effectiveTargetClauseId}
        onSelectTargetClause={setTargetClauseId}
        availableClauses={availableClauses}
        parameters={parameters}
        onChangeParameters={setParameters}
        experimentalOptIn={experimentalOptIn}
        onToggleOptIn={setExperimentalOptIn}
        onExecute={handleExecute}
        executing={executing}
      />

      {/* 3–6. Experiment Results View (When available) */}
      {caseResult ? (
        <div className="space-y-4 pt-2">
          <DetectionOutcomePanel caseResult={caseResult} />
          <OriginalVsPerturbedView caseResult={caseResult} />
          <ChannelResponseComparison caseResult={caseResult} />
          <RuleDetectionPanel caseResult={caseResult} />
          <ScenarioEvidenceInspector caseResult={caseResult} />
        </div>
      ) : (
        <RedTeamEmptyState
          onQuickLaunch={(type) => {
            handleSelectType(type);
            setExperimentalOptIn(true);
          }}
        />
      )}

      {/* 7. Methodology & Limitations Footer */}
      <ExperimentLimitations />
    </div>
  );
}
