"use client";

import React, { useEffect, useState, useMemo } from "react";
import { CompatibilityArtifact, SelectedCell } from "./types";
import { ClauseTypeSelector } from "./ClauseTypeSelector";
import { CompatibilityMatrixLegend } from "./CompatibilityMatrixLegend";
import { CompatibilityHeatmap } from "./CompatibilityHeatmap";
import { CompatibilityDetails } from "./CompatibilityDetails";
import { CompatibilityMethodology } from "./CompatibilityMethodology";
import { Activity, AlertTriangle, RefreshCw, Cpu } from "lucide-react";

// Predefined indices for curated presets based on LEDGAR centroids
const CORE_COMMERCIAL_INDICES = [41, 1, 2, 16, 56, 37, 48, 60, 10, 14, 19, 24]; // 12 categories
const BOILERPLATE_INDICES = [2, 1, 41, 57, 56, 14, 20, 39, 3, 47]; // 10 categories

export function LearnedCompatibilityWorkspace() {
  const [artifact, setArtifact] = useState<CompatibilityArtifact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [presetFilter, setPresetFilter] = useState<"all" | "core" | "boilerplate">("core");
  const [selectedCell, setSelectedCell] = useState<SelectedCell | null>(null);

  // Load the frozen model compatibility matrix artifact
  const fetchArtifactData = async (cancelledRef: { current: boolean }) => {
    try {
      const res = await fetch("/research/learned_clause_pair_compatibility.json");
      if (!res.ok) {
        throw new Error(`Failed to load compatibility artifact (HTTP ${res.status}: ${res.statusText})`);
      }
      const data: CompatibilityArtifact = await res.json();
      if (!cancelledRef.current) {
        setArtifact(data);

        // Default select the first cell in core preset if available
        if (data.clause_types && data.clause_types.length > 1) {
          const aIdx = CORE_COMMERCIAL_INDICES[0];
          const sIdx = CORE_COMMERCIAL_INDICES[1];
          const aName = data.clause_types[aIdx]?.name || "Entire Agreement";
          const sName = data.clause_types[sIdx]?.name || "Governing Laws";
          setSelectedCell({
            antecedentIndex: aIdx,
            successorIndex: sIdx,
            antecedentName: aName,
            successorName: sName,
            score: data.compatibility_matrix[aIdx]?.[sIdx] ?? 0.35,
            reverseScore: data.compatibility_matrix[sIdx]?.[aIdx] ?? 0.35,
          });
        }
      }
    } catch (err: unknown) {
      if (!cancelledRef.current) {
        const msg = err instanceof Error ? err.message : "Failed to load learned clause-pair compatibility artifact.";
        console.error("Compatibility matrix load error:", msg);
        setError(msg);
      }
    } finally {
      if (!cancelledRef.current) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const isCancelled = { current: false };
    queueMicrotask(() => {
      if (!isCancelled.current) {
        fetchArtifactData(isCancelled);
      }
    });
    return () => {
      isCancelled.current = true;
    };
  }, []);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    fetchArtifactData({ current: false });
  };

  // Filtered indices to display based on presets and search query
  const filteredIndices = useMemo(() => {
    if (!artifact) return [];

    let baseIndices: number[] = [];
    if (presetFilter === "core") {
      baseIndices = CORE_COMMERCIAL_INDICES.filter((i) => i < artifact.clause_types.length);
    } else if (presetFilter === "boilerplate") {
      baseIndices = BOILERPLATE_INDICES.filter((i) => i < artifact.clause_types.length);
    } else {
      // all
      baseIndices = artifact.clause_types.map((_, idx) => idx);
    }

    if (!searchQuery.trim()) {
      return baseIndices;
    }

    const q = searchQuery.toLowerCase().trim();
    // If user searches, search across ALL clause types to give full flexibility
    return artifact.clause_types
      .map((item, idx) => ({ item, idx }))
      .filter(({ item }) => item.name.toLowerCase().includes(q))
      .map(({ idx }) => idx);
  }, [artifact, presetFilter, searchQuery]);

  if (loading) {
    return (
      <div
        id="flow-workspace-loading"
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-lg)",
          padding: "3rem 1.5rem",
          textAlign: "center",
          color: "var(--color-text-secondary)",
        }}
      >
        <Activity size={32} className="spin-slow" style={{ margin: "0 auto 1rem", color: "var(--color-accent)" }} />
        <h4 style={{ margin: "0 0 0.5rem", color: "var(--color-text-primary)" }}>
          Loading Learned Clause-Pair Compatibility Map...
        </h4>
        <p style={{ margin: 0, fontSize: "0.85rem" }}>
          Reading frozen model evaluation artifact (4,356 ordered pairs across 66 LEDGAR centroids).
        </p>
      </div>
    );
  }

  if (error || !artifact) {
    return (
      <div
        id="flow-workspace-error"
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--sev-high-border, #dc2626)",
          borderRadius: "var(--radius-lg)",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <AlertTriangle size={32} style={{ color: "var(--sev-high-text, #dc2626)", margin: "0 auto 0.75rem" }} />
        <h4 style={{ margin: "0 0 0.5rem", color: "var(--color-text-primary)" }}>
          Learned Compatibility Map Unavailable
        </h4>
        <p style={{ margin: "0 0 1rem", color: "var(--color-text-secondary)", fontSize: "0.85rem" }}>
          {error || "Artifact data could not be verified."}
        </p>
        <button className="btn btn-primary" onClick={handleRetry} style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem" }}>
          <RefreshCw size={14} /> Retry Loading Artifact
        </button>
      </div>
    );
  }

  return (
    <div id="learned-compatibility-workspace" style={{ marginTop: "1rem" }}>
      {/* Workspace Header */}
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-lg)",
          padding: "1.25rem 1.5rem",
          marginBottom: "1rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.75rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
              <span
                style={{
                  fontSize: "0.7rem",
                  textTransform: "uppercase",
                  fontWeight: 700,
                  letterSpacing: "0.05em",
                  background: "var(--color-surface-sunken, rgba(37,99,235,0.1))",
                  color: "var(--color-accent)",
                  padding: "0.2rem 0.5rem",
                  borderRadius: "4px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.3rem",
                }}
              >
                <Cpu size={12} /> Pretrained Model Artifact (Track A)
              </span>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
                Schema v{artifact.schema_version}
              </span>
            </div>
            <h3 style={{ margin: "0.25rem 0 0.4rem", fontSize: "1.2rem", color: "var(--color-text-primary)", fontWeight: 700 }}>
              Learned Clause-Pair Compatibility Map
            </h3>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--color-text-secondary)", maxWidth: "850px", lineHeight: "1.4" }}>
              Visualizes the frozen Channel B neural coherence head (<code>CoherenceScorerHead</code>, 3,072-dim pairwise features) evaluated over reference LEDGAR centroid vectors. Cell scores represent directional sequential compatibility P(c_i → c_j).
            </p>
          </div>

          <div
            style={{
              textAlign: "right",
              fontSize: "0.75rem",
              color: "var(--color-text-secondary)",
              background: "var(--color-bg)",
              padding: "0.5rem 0.75rem",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--color-border)",
            }}
          >
            <div><strong>Total Categories:</strong> {artifact.dimensions.num_clause_types} (LEDGAR)</div>
            <div><strong>Total Evaluated Pairs:</strong> {artifact.dimensions.num_ordered_pairs}</div>
            <div><strong>Mean Score:</strong> {artifact.summary_statistics.mean_score.toFixed(4)}</div>
          </div>
        </div>
      </div>

      {/* Selector & Filters */}
      <ClauseTypeSelector
        clauseTypes={artifact.clause_types}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        presetFilter={presetFilter}
        onPresetChange={setPresetFilter}
        selectedIndicesCount={filteredIndices.length}
      />

      {/* Score Legend */}
      <CompatibilityMatrixLegend
        minScore={artifact.summary_statistics.min_score}
        maxScore={artifact.summary_statistics.max_score}
        meanScore={artifact.summary_statistics.mean_score}
      />

      {/* Selected Cell Inspector */}
      <CompatibilityDetails
        selectedCell={selectedCell}
        onClearSelection={() => setSelectedCell(null)}
      />

      {/* Interactive Heatmap Grid */}
      <CompatibilityHeatmap
        clauseTypes={artifact.clause_types}
        matrix={artifact.compatibility_matrix}
        selectedIndices={filteredIndices}
        selectedCell={selectedCell}
        onSelectCell={setSelectedCell}
        minScore={artifact.summary_statistics.min_score}
        maxScore={artifact.summary_statistics.max_score}
      />

      {/* Technical Methodology & Provenance Disclosure */}
      <CompatibilityMethodology artifact={artifact} />
    </div>
  );
}
