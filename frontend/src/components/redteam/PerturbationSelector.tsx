"use client";

import React from "react";
import { PerturbationType } from "./types";
import {
  Move,
  ArrowLeftRight,
  Copy,
  CopyPlus,
  Unlink,
  FileQuestion,
  CalendarClock,
  Trash2,
  ShieldCheck,
  Layers,
} from "lucide-react";

interface PerturbationSelectorProps {
  selectedType: PerturbationType;
  onSelectType: (type: PerturbationType) => void;
  disabled?: boolean;
}

interface TaxonomyOption {
  type: PerturbationType;
  title: string;
  categoryCode: string;
  shortDesc: string;
  expectedDetector: string;
  icon: React.ComponentType<{ size?: number; className?: string; style?: React.CSSProperties }>;
  tagColor: string;
}

const TAXONOMY: TaxonomyOption[] = [
  {
    type: "P1_DISPLACEMENT",
    title: "Clause Displacement",
    categoryCode: "P1",
    shortDesc: "Move an existing clause to a distant or subtle target position.",
    expectedDetector: "Channel B Discourse Model",
    icon: Move,
    tagColor: "rt-tag rt-tag-blue",
  },
  {
    type: "P2_SWAP",
    title: "Clause Swapping",
    categoryCode: "P2",
    shortDesc: "Pairwise transposition of adjacent or non-adjacent clauses.",
    expectedDetector: "Channel B Discourse Model",
    icon: ArrowLeftRight,
    tagColor: "rt-tag rt-tag-indigo",
  },
  {
    type: "P3_EXACT_DUPLICATION",
    title: "Exact Duplication",
    categoryCode: "P3",
    shortDesc: "Duplicate an authoritative clause into an unexpected slot.",
    expectedDetector: "Descriptive (Dedicated detector unavailable)",
    icon: Copy,
    tagColor: "rt-tag rt-tag-amber",
  },
  {
    type: "P4_NEAR_DUPLICATION",
    title: "Near-Duplicate Variant",
    categoryCode: "P4",
    shortDesc: "Deterministic lexical synonym substitutions of legal terms.",
    expectedDetector: "Channel A OOD (Exploratory)",
    icon: CopyPlus,
    tagColor: "rt-tag rt-tag-amber",
  },
  {
    type: "P5_BROKEN_REFERENCE",
    title: "Broken Cross-Reference",
    categoryCode: "P5",
    shortDesc: "Mutate internal citations to cite undeclared section numbers.",
    expectedDetector: "CrossReferenceChecker (spaCy)",
    icon: Unlink,
    tagColor: "rt-tag rt-tag-red",
  },
  {
    type: "P6_MISSING_EXHIBIT",
    title: "Missing Exhibit Citation",
    categoryCode: "P6",
    shortDesc: "Mutate exhibit reference to undeclared exhibit target.",
    expectedDetector: "CrossReferenceChecker (spaCy)",
    icon: FileQuestion,
    tagColor: "rt-tag rt-tag-red",
  },
  {
    type: "P7_DATE_INVERSION",
    title: "Date Chronology Inversion",
    categoryCode: "P7",
    shortDesc: "Inject temporal contradiction (e.g. Termination prior to Effective).",
    expectedDetector: "DateLogicChecker (dateparser)",
    icon: CalendarClock,
    tagColor: "rt-tag rt-tag-purple",
  },
  {
    type: "P8_DELETION",
    title: "Clause Deletion",
    categoryCode: "P8",
    shortDesc: "Delete clause with verifiable dependency consequence.",
    expectedDetector: "CrossReferenceChecker / Descriptive",
    icon: Trash2,
    tagColor: "rt-tag rt-tag-amber",
  },
  {
    type: "P9_NEGATIVE_CONTROL",
    title: "Clean Negative Control",
    categoryCode: "P9",
    shortDesc: "Untouched document to check prediction stability and baseline flags.",
    expectedDetector: "Expect unchanged outputs",
    icon: ShieldCheck,
    tagColor: "rt-tag rt-tag-emerald",
  },
  {
    type: "P10_COMBINED",
    title: "Compound Perturbation",
    categoryCode: "P10",
    shortDesc: "Multi-disturbance interaction (e.g. Displacement + Dangling Reference).",
    expectedDetector: "Multi-Detector Ensemble",
    icon: Layers,
    tagColor: "rt-tag rt-tag-cyan",
  },
];

export function PerturbationSelector({
  selectedType,
  onSelectType,
  disabled = false,
}: PerturbationSelectorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
          1. Select Perturbation Scenario (Taxonomy P1–P10)
        </label>
        <span className="text-xs text-slate-500 font-mono">10 Standard Categories</span>
      </div>

      <div className="rt-taxonomy-grid">
        {TAXONOMY.map((item) => {
          const Icon = item.icon;
          const isSelected = selectedType === item.type;
          return (
            <button
              key={item.type}
              type="button"
              id={`redteam-type-${item.categoryCode.toLowerCase()}`}
              disabled={disabled}
              onClick={() => onSelectType(item.type)}
              className={`rt-type-btn ${isSelected ? "active" : ""}`}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.4rem" }}>
                  <span className={item.tagColor}>
                    {item.categoryCode}
                  </span>
                  <Icon
                    size={16}
                    style={{ color: isSelected ? "var(--color-accent)" : "var(--color-text-muted)" }}
                  />
                </div>
                <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--color-text-primary)", marginBottom: "0.25rem" }}>
                  {item.title}
                </div>
                <p style={{ fontSize: "0.72rem", color: "var(--color-text-secondary)", lineHeight: 1.4, margin: 0 }}>
                  {item.shortDesc}
                </p>
              </div>

              <div style={{ marginTop: "0.6rem", paddingTop: "0.4rem", borderTop: "1px solid var(--color-border-subtle)" }}>
                <span style={{ fontSize: "0.68rem", color: "var(--color-text-muted)", fontFamily: "monospace", display: "block" }}>
                   {item.expectedDetector}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
