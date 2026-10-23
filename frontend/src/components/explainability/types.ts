/**
 * frontend/src/components/explainability/types.ts
 * Type definitions for the Phase 4B Explainability Workspace.
 */

import { DocumentResult } from "../review/types";

export interface IntegratedGradientsPayload {
  tokens: string[];
  attributions: number[];
  target_score: number;
  baseline_score: number;
}

export interface SensitivityPayload {
  neighbor_clause_id: string;
  neighbor_position: "prev" | "next" | "none";
  original_score: number;
  perturbed_score: number;
  score_delta: number;
  perturbation_method: string;
}

export interface NearestNeighborItem {
  neighbor_clause_id: string;
  source_document: string;
  similarity: number;
  label?: string;
}

export interface ClaimScopeData {
  what_this_shows: string;
  what_this_does_not_show: string;
}

export interface XaiResponse {
  explanation_id: string;
  doc_id: string;
  clause_id: string;
  explanation_type: "INTEGRATED_GRADIENTS" | "SENSITIVITY" | "NEAREST_NEIGHBOR";
  model_version: string;
  timestamp: string;
  claim_scope: ClaimScopeData;
  ig_payload?: IntegratedGradientsPayload;
  sensitivity_payload?: SensitivityPayload;
  nn_payload?: NearestNeighborItem[];
}

export interface ExplainabilityWorkspaceProps {
  documentResult: DocumentResult | null;
  selectedClauseId: string;
  backendUrl: string;
  apiKey: string;
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
  onNavigateToFeedback?: () => void;
  onNavigateToUpload?: () => void;
}
