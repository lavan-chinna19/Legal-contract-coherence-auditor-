"""
src/scoring/severity.py — Decision-Support Ranking Layer for Legal Anomaly Auditing (Prompt 10).
Combines ensembled score, cross-channel agreement (Channel A vs B), and conformal interval width
into documented High / Medium / Low / Clean severity tiers.
"""
from dataclasses import dataclass, asdict
from typing import Tuple, Optional, Dict, Any


@dataclass
class SeverityAssessment:
    """
    Structured outcome of the decision-support ranking layer for a single clause.
    """
    severity: str                   # "HIGH" | "MEDIUM" | "LOW" | "CLEAN"
    is_anomaly: bool                # True for HIGH/MEDIUM
    cross_channel_agreement: float  # [0.0, 1.0]: 1.0 - |score_A - score_B|
    agreement_type: str             # "CONCORDANT_ANOMALY" | "CONCORDANT_CLEAN" | "CHANNEL_A_DOMINANT" | "CHANNEL_B_DOMINANT"
    interval_width: Optional[float] # Width of conformal prediction interval
    severity_justification: str     # Auditor-facing rationale

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_cross_channel_agreement(
    score_a: float,
    score_b: float,
    threshold: float = 0.50
) -> Tuple[float, str]:
    """
    Computes cross-channel concordance between Channel A (semantic OOD) and Channel B (discourse transition).
    
    Returns:
        Tuple of (agreement_magnitude [0.0, 1.0], agreement_type)
    """
    agreement_magnitude = round(float(max(0.0, min(1.0, 1.0 - abs(score_a - score_b)))), 4)

    is_a_anom = score_a >= threshold
    is_b_anom = score_b >= threshold

    if is_a_anom and is_b_anom:
        agreement_type = "CONCORDANT_ANOMALY"
    elif (not is_a_anom) and (not is_b_anom):
        agreement_type = "CONCORDANT_CLEAN"
    elif is_a_anom and (not is_b_anom):
        agreement_type = "CHANNEL_A_DOMINANT"
    else:
        agreement_type = "CHANNEL_B_DOMINANT"

    return agreement_magnitude, agreement_type


class SeverityRanker:
    """
    Decision-support rule engine mapping multi-channel evidence and uncertainty intervals
    into calibrated severity classifications.
    
    Documented Threshold Defaults:
    -------------------------------
    - HIGH_THRESHOLD = 0.65: Combined score requiring dual-channel corroboration or strong single-channel failure.
    - HIGH_SINGLE_THRESHOLD = 0.85: Extreme single-channel failure warranting HIGH even without cross-channel agreement.
    - MED_THRESHOLD = 0.50: Composite anomaly score triggering actionable auditor review.
    - MED_SINGLE_THRESHOLD = 0.70: Distinct single-channel breach (e.g. sharp discourse break or OOD injection).
    - LOW_THRESHOLD = 0.35: Sub-threshold noise / mild contextual deviation.
    - CONF_LOWER_BOUND_THRESHOLD = 0.40: Conformal interval lower bound guaranteeing high baseline risk.
    """

    def __init__(
        self,
        high_threshold: float = 0.65,
        high_single_threshold: float = 0.85,
        med_threshold: float = 0.50,
        med_single_threshold: float = 0.70,
        low_threshold: float = 0.35,
        channel_anom_threshold: float = 0.50,
        conf_lower_bound_threshold: float = 0.40
    ):
        self.high_threshold = high_threshold
        self.high_single_threshold = high_single_threshold
        self.med_threshold = med_threshold
        self.med_single_threshold = med_single_threshold
        self.low_threshold = low_threshold
        self.channel_anom_threshold = channel_anom_threshold
        self.conf_lower_bound_threshold = conf_lower_bound_threshold

    def assess_clause(
        self,
        channel_a_score: float,
        channel_b_score: float,
        combined_score: float,
        confidence_interval: Optional[Tuple[float, float]] = None
    ) -> SeverityAssessment:
        """
        Assesses severity for a single clause by combining ensemble score, cross-channel agreement,
        and conformal interval width.
        """
        agreement, agreement_type = compute_cross_channel_agreement(
            channel_a_score,
            channel_b_score,
            threshold=self.channel_anom_threshold
        )

        interval_width = None
        ci_lower = None
        if confidence_interval is not None and len(confidence_interval) == 2:
            ci_lower, ci_upper = confidence_interval
            interval_width = round(float(ci_upper - ci_lower), 4)

        # Decision Logic:
        # 1. HIGH Severity Criteria:
        #    - Combined >= 0.65 with dual-channel concordance (both channels flag)
        #    - Combined >= 0.75 (extreme composite failure)
        #    - Single channel >= 0.85 with combined >= 0.60
        #    - Conformal interval lower bound >= 0.40 with Combined >= 0.60
        if (
            (combined_score >= self.high_threshold and agreement_type == "CONCORDANT_ANOMALY")
            or (combined_score >= 0.75)
            or (max(channel_a_score, channel_b_score) >= self.high_single_threshold and combined_score >= 0.60)
            or (ci_lower is not None and ci_lower >= self.conf_lower_bound_threshold and combined_score >= 0.60)
        ):
            severity = "HIGH"
            is_anomaly = True
            if agreement_type == "CONCORDANT_ANOMALY":
                justification = (
                    f"High confidence dual-channel corroboration (Score A={channel_a_score:.2f}, "
                    f"Score B={channel_b_score:.2f}, Agreement={agreement:.2f})"
                )
            elif channel_a_score >= channel_b_score:
                justification = (
                    f"Severe semantic out-of-distribution anomaly (Score A={channel_a_score:.2f} >= "
                    f"{self.high_single_threshold:.2f})"
                )
            else:
                justification = (
                    f"Severe discourse transition breakdown (Score B={channel_b_score:.2f} >= "
                    f"{self.high_single_threshold:.2f})"
                )

        # 2. MEDIUM Severity Criteria:
        #    - Combined >= 0.50
        #    - Single-channel anomaly >= 0.70 (Channel A or Channel B dominant)
        elif (
            combined_score >= self.med_threshold
            or channel_a_score >= self.med_single_threshold
            or channel_b_score >= self.med_single_threshold
        ):
            severity = "MEDIUM"
            is_anomaly = True
            if agreement_type == "CHANNEL_A_DOMINANT":
                justification = (
                    f"Noticeable semantic shift flagged by Channel A (Score A={channel_a_score:.2f} >= {self.med_single_threshold:.2f})"
                )
            elif agreement_type == "CHANNEL_B_DOMINANT":
                justification = (
                    f"Structural transition break flagged by Channel B (Score B={channel_b_score:.2f} >= {self.med_single_threshold:.2f})"
                )
            else:
                justification = (
                    f"Composite anomaly score ({combined_score:.2f} >= {self.med_threshold:.2f})"
                )

        # 3. LOW Severity Criteria:
        #    - Combined >= 0.35
        elif combined_score >= self.low_threshold:
            severity = "LOW"
            is_anomaly = False
            justification = f"Minor deviation ({combined_score:.2f}) below actionable anomaly threshold"

        # 4. CLEAN Criteria:
        else:
            severity = "CLEAN"
            is_anomaly = False
            justification = "Scores well within normal legal contract distribution envelope"

        # Add conformal note if interval is wide/tight
        if interval_width is not None and interval_width < 0.60:
            justification += f" [Tight CI width: {interval_width:.2f}]"

        return SeverityAssessment(
            severity=severity,
            is_anomaly=is_anomaly,
            cross_channel_agreement=agreement,
            agreement_type=agreement_type,
            interval_width=interval_width,
            severity_justification=justification
        )
