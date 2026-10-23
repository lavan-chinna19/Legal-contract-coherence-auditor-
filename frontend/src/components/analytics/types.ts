import { DocumentResult, ClauseResult, RuleFlag } from "../review/types";

export type { DocumentResult, ClauseResult, RuleFlag };

export interface AnalyticsWorkspaceProps {
  documentResult: DocumentResult | null;
  selectedClauseId: string;
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
  onNavigateToXai?: () => void;
  onNavigateToFeedback?: () => void;
}

export interface AnalyticsSummaryProps {
  documentResult: DocumentResult;
}

export interface ClauseScoreDistributionProps {
  clauses: ClauseResult[];
  selectedClauseId: string;
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
}

export interface SeverityDistributionProps {
  clauses?: ClauseResult[];
  totalClauses: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  onSelectSeverityFilter?: (severity: string) => void;
}

export interface ChannelEvidenceComparisonProps {
  selectedClause?: ClauseResult;
}

export interface RuleFindingsSummaryProps {
  ruleFlags: RuleFlag[];
  clauses: ClauseResult[];
  onSelectClauseId: (clauseId: string) => void;
  onNavigateToReview?: () => void;
}

export interface CalibrationTransparencyProps {
  scoringResult: DocumentResult["scoring_result"];
  selectedClause?: ClauseResult;
}
