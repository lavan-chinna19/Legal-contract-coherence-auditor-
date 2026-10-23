/**
 * frontend/src/components/flow/types.ts
 * Type definitions for the Learned Clause-Pair Compatibility Map (Phase 4B).
 */

export interface ClauseTypeItem {
  id: string;
  numeric_id: number;
  name: string;
  matrix_index: number;
}

export interface CompatibilityArtifact {
  schema_version: string;
  milestone: string;
  title: string;
  generated_at: string;
  script_version: string;
  provenance: {
    model_architecture: string;
    checkpoint_path: string;
    checkpoint_sha256: string;
    checkpoint_size_bytes: number;
    centroids_path: string;
    centroids_sha256: string;
    centroids_size_bytes: number;
    reference_corpus: string;
    embedding_model: string;
  };
  score_semantics: {
    quantity: string;
    mathematical_formula: string;
    domain: string;
    orientation: string;
    interpretation: string;
    anomaly_relation: string;
    directional: boolean;
    row_stochastic_normalized: boolean;
    normalization_disclosure: string;
  };
  dimensions: {
    num_clause_types: number;
    num_ordered_pairs: number;
    rows_meaning: string;
    columns_meaning: string;
  };
  summary_statistics: {
    min_score: number;
    max_score: number;
    mean_score: number;
    diagonal_self_mean: number;
    mean_directional_asymmetry: number;
  };
  clause_types: ClauseTypeItem[];
  compatibility_matrix: number[][];
}

export interface SelectedCell {
  antecedentIndex: number;
  successorIndex: number;
  antecedentName: string;
  successorName: string;
  score: number;
  reverseScore: number;
}
