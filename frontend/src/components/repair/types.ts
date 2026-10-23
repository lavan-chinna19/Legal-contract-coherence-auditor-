/**
 * frontend/src/components/repair/types.ts
 * Types for Phase 4C Counterfactual Repositioning Workspace.
 */

export interface RepositionCandidate {
  position_idx: number;
  rank: number;
  relative_placement: string;
  preceding_clause_id?: string | null;
  succeeding_clause_id?: string | null;
  mean_combined_score: number;
  mean_channel_b_score: number;
  clause_channel_b_score: number;
  objective_delta: number;
  is_current_position: boolean;
  is_recommended: boolean;
}

export interface RepositionResponse {
  doc_id: string;
  target_clause_id: string;
  target_clause_idx: number;
  total_clauses: number;
  original_mean_combined_score: number;
  original_target_sb: number;
  best_candidate_idx: number | null;
  best_objective_delta: number;
  is_abstaining: boolean;
  abstention_reason: string | null;
  warning_notice: string;
  model_provenance: string;
  primary_objective_name: string;
  candidates: RepositionCandidate[];
  optimization_verified: boolean;
  evaluation_time_ms: number;
}

export interface CounterfactualRepairWorkspaceProps {
  docId: string;
  targetClauseId: string;
  backendUrl: string;
  apiKey: string;
  onClose: () => void;
  onNavigateToXai?: () => void;
  onNavigateToFeedback?: () => void;
}
