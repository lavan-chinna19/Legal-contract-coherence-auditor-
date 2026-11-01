export interface DependencyGraphResult {
  status: string; scope: string; edges: unknown[];
  findings: { source_clause_id: string; reference: string; reason: string; target?: { clause_id: string; section_id: string } }[];
  reviews: DependencyGraphResult["findings"];
}
export interface ChannelAEvidence {
  nearest_centroid_label: string;
  centroid_distance: number;
  is_ood: boolean;
  top_k_distances?: Record<string, number>;
}

export interface ChannelBEvidence {
  incoming_prob?: number;
  outgoing_prob?: number;
  incoming_anomaly?: number;
  outgoing_anomaly?: number;
  prev_clause_id?: string;
  next_clause_id?: string;
}

export interface ClauseResult {
  clause_id: string;
  doc_id: string;
  sequence_idx: number;
  text_preview: string;
  channel_a_score: number;
  channel_b_score: number;
  combined_score: number;
  channel_a_evidence: ChannelAEvidence;
  channel_b_evidence: ChannelBEvidence;
  is_anomaly: boolean;
  severity: "HIGH" | "MEDIUM" | "LOW" | string;
  confidence_interval?: [number, number];
  calibration_source: string;
  cross_channel_agreement: number;
  agreement_type: string;
  interval_width?: number;
  severity_justification?: string;
  source_label?: string;
}

export interface RuleFlag {
  flag_id: string;
  doc_id?: string;
  flag_type: string;
  category?: string;
  severity: string;
  title: string;
  description: string;
  clause_id?: string;
  involved_clause_ids?: string[];
  evidence?: Record<string, unknown>;
  claim_scope?: Record<string, unknown>;
}

export interface DocumentResult {
  metadata?: { source_text?: string; analysis_state?: string; document_name?: string; dependency_graph?: DependencyGraphResult;
    clause_inventory?: { clause_id: string; doc_id: string; text: string; sequence_idx: number; char_start: number; char_end: number }[] };
  doc_id: string;
  total_clauses: number;
  ml_anomaly_count: number;
  rule_violation_count: number;
  total_flags: number;
  high_severity_count: number;
  medium_severity_count: number;
  low_severity_count: number;
  scoring_result: {
    mean_combined_score: number;
    max_combined_score: number;
    clauses: ClauseResult[];
    calibration_source: string;
  };
  rule_flags: RuleFlag[];
}

export type ClauseAlignmentStatus =
  | "VERIFIED_FULL_TEXT"
  | "PREVIEW_ONLY_AMBIGUOUS"
  | "PREVIEW_ONLY_UNMATCHED"
  | "PREVIEW_ONLY_INSUFFICIENT_EVIDENCE";

export interface ClauseAlignmentResult {
  clauseId: string;
  sequenceIdx: number;
  status: ClauseAlignmentStatus;
  displayText: string;
  sourceStart?: number;
  sourceEnd?: number;
  explanation: string;
}

export interface EnrichedClause extends ClauseResult {
  full_text: string;
  is_full_text: boolean;
  alignment_status: ClauseAlignmentStatus;
  alignment_explanation: string;
  source_start?: number;
  source_end?: number;
  associated_rules: RuleFlag[];
}

export type SeverityFilter = "ALL" | "FLAGGED" | "HIGH" | "MEDIUM" | "LOW" | "CLEAN";
