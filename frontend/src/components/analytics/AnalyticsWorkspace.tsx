"use client";
import { DocumentResult } from "./types";
import { AnalyticsSummary } from "./AnalyticsSummary";
import { ClauseScoreDistribution } from "./ClauseScoreDistribution";
import { SeverityDistribution } from "./SeverityDistribution";
import { ChannelEvidenceComparison } from "./ChannelEvidenceComparison";
import { RuleFindingsSummary } from "./RuleFindingsSummary";
import { CalibrationTransparency } from "./CalibrationTransparency";
import { AnalyticsEmptyState } from "./AnalyticsEmptyState";
interface AnalyticsWorkspaceProps { documentResult: DocumentResult | null; selectedClauseId: string; onSelectClauseId: (id: string) => void; onNavigateToReview?: () => void; onNavigateToUpload?: () => void; onNavigateToXai?: () => void; onNavigateToFeedback?: () => void }
export function AnalyticsWorkspace({ documentResult, selectedClauseId, onSelectClauseId, onNavigateToReview, onNavigateToUpload }: AnalyticsWorkspaceProps) {
  if (!documentResult) return <AnalyticsEmptyState onNavigateToUpload={onNavigateToUpload} />;
  const clauses = documentResult.scoring_result.clauses;
  const selectedClause = clauses.find(c => c.clause_id === selectedClauseId) || clauses[0];
  return <div className="stack" aria-label="Current audit analytics"><AnalyticsSummary documentResult={documentResult} />


          {/* 2. Interactive Clause Anomaly Score Distribution (Timeline / Sequence) */}
          <ClauseScoreDistribution
            clauses={clauses}
            selectedClauseId={selectedClauseId}
            onSelectClauseId={onSelectClauseId}
            onNavigateToReview={onNavigateToReview}
          />

          {/* 3. Dual-Column Diagnostic Section: Severity Distribution + Channel Evidence */}
          <div
            className="analytics-two-col-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
              gap: "1.25rem",
              alignItems: "stretch",
            }}
          >
            <SeverityDistribution
              totalClauses={documentResult.total_clauses}
              highCount={clauses.filter(c => c.severity === "HIGH").length}
              mediumCount={clauses.filter(c => c.severity === "MEDIUM").length}
              lowCount={clauses.filter(c => c.severity === "LOW").length}
            />

            <ChannelEvidenceComparison selectedClause={selectedClause} />
          </div>

          {/* 4. Deterministic Rule Violations Breakdown */}
          <RuleFindingsSummary
            ruleFlags={documentResult.rule_flags ?? []}
            clauses={clauses}
            onSelectClauseId={onSelectClauseId}
            onNavigateToReview={onNavigateToReview}
          />

          {/* 5. Calibration Transparency & Methodological Limitations */}
          <details className="card"><summary>Calibration and uncertainty</summary><CalibrationTransparency
            scoringResult={documentResult.scoring_result}
            selectedClause={selectedClause}
          /></details>
</div>;
}
