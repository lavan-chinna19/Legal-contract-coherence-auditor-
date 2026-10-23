/**
 * frontend/src/components/redteam/types.ts
 * Type definitions for Self Red-Team Robustness Laboratory (Phase 4D).
 */

export type PerturbationType =
  | "P1_DISPLACEMENT"
  | "P2_SWAP"
  | "P3_EXACT_DUPLICATION"
  | "P4_NEAR_DUPLICATION"
  | "P5_BROKEN_REFERENCE"
  | "P6_MISSING_EXHIBIT"
  | "P7_DATE_INVERSION"
  | "P8_DELETION"
  | "P9_NEGATIVE_CONTROL"
  | "P10_COMBINED";

export type PerturbationDifficulty =
  | "LEVEL_1_STRAIGHTFORWARD"
  | "LEVEL_2_MODERATE"
  | "LEVEL_3_DIFFICULT";

export type DetectionStatus =
  | "DETECTED"
  | "NOT_DETECTED"
  | "INCONCLUSIVE"
  | "NOT_APPLICABLE"
  | "INVALID_SCENARIO"
  | "EXPERIMENT_FAILED";

export interface RedTeamConditionResult {
  condition_name: string;
  target_property: string;
  expected_value: unknown;
  observed_value: unknown;
  is_satisfied: boolean;
  description: string;
}

export interface RedTeamOracleResponse {
  valid_transformation: boolean;
  oracle_condition: string;
  expected_detector: string;
  ground_truth_supported: boolean;
  ground_truth_reason: string;
  affected_clause_ids: string[];
  eligible_for_strict_evaluation: boolean;
  conditions: RedTeamConditionResult[];
}

export interface ClausePreviewItem {
  clause_id: string;
  sequence_idx: number;
  text: string;
  label?: string;
}

export interface RedTeamCaseResponse {
  scenario_id: string;
  perturbation_type: PerturbationType;
  difficulty: PerturbationDifficulty;
  source_doc_id: string;
  original_checksum: string;
  perturbed_checksum: string;
  detection_status: DetectionStatus;
  attribution_valid: boolean;
  original_mean_combined: float;
  perturbed_mean_combined: float;
  delta_mean_combined: float;
  original_anomaly_count: number;
  perturbed_anomaly_count: number;
  delta_anomaly_count: number;
  original_rule_flag_count: number;
  perturbed_rule_flag_count: number;
  new_rule_flags: Array<{
    flag_id?: string;
    flag_type?: string;
    severity?: string;
    title?: string;
    description?: string;
    clause_id?: string;
    evidence?: Record<string, unknown>;
  }>;
  mean_channel_a_delta: number;
  mean_channel_b_delta: number;
  max_affected_clause_b_delta: number;
  channel_a_only_delta: number;
  channel_b_only_delta: number;
  dual_channel_combined_delta: number;
  affected_clause_ids: string[];
  oracle_result: RedTeamOracleResponse;
  failure_category?: string;
  failure_explanation?: string;
  execution_time_ms: number;
  original_clauses_preview: ClausePreviewItem[];
  perturbed_clauses_preview: ClausePreviewItem[];
}

type float = number;

export interface CanonicalScenarioDefinition {
  scenario_id: string;
  perturbation_type: PerturbationType;
  difficulty: PerturbationDifficulty;
  source_fixture_id: "SYNTH_DOC_01_MSA" | "SYNTH_DOC_02_SLA";
  title: string;
  description: string;
  expected_detector: string;
  target_clause_ids: string[];
  parameters: Record<string, unknown>;
  limitations: string;
}
