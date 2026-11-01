# LexAudit Phase 4C-A — Threshold Selection & Provenance Audit

## 1. Threshold Classification: `UNVERIFIED_HEURISTIC_THRESHOLD`
The default abstention threshold `min_delta_threshold = 0.005` ($0.5\%$ aggregate coherence improvement) was proposed as an engineering safety margin in Phase 4A/4C.

### Provenance Audit Findings:
1. **No Supervised Calibration on Dev Set**: Historical investigation confirms that $\delta = 0.005$ was NOT fit via ROC optimization, Platt scaling, or cross-validated search on a pre-declared development set.
2. **Heuristic Noise Filter**: The threshold functions as an empirical filter to prevent recommending tiny, noisy position swaps ($< 0.0015$ delta), which are common in legal boilerplate.
3. **Scientific Label**: In academic reporting, this parameter must be strictly classified as an `UNVERIFIED_HEURISTIC_THRESHOLD`, not a calibrated statistical bound.

## 2. Sensitivity Analysis Summary
Evaluated across $\delta \in \{0.001, 0.0025, 0.005, 0.01, 0.02\}$:
- **Threshold $\ge 0.0025$** completely suppresses false repairs on clean unperturbed contracts ($0.0\%$ false repairs, $100\%$ abstention).
- **Threshold $< 0.0015$** allows minor boilerplate permutations with deltas $\approx 0.0003 - 0.0013$ to be surfaced as recommended moves.
- **Threshold $0.005$** provides a conservative operational operating point without sacrificing Top-3 candidate recovery.
