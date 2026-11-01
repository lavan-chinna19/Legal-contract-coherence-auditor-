# LexAudit Phase 4D Metric Definitions

### 1. Structural Sensitivity (P1, P2)
- **Mean Channel B Delta**: Average increase in Channel B transition score across affected boundary slots.
- **Affected Boundary Detection Rate**: Proportion of structural moves causing Channel B transition increase $\ge 0.08$ or newly flagged anomalies.

### 2. Rule Precision, Recall, and F1 (P5, P6, P7, P8)
- **True Positive (TP)**: Injected rule violation detected and attributed to the affected clause/scope.
- **False Negative (FN)**: Injected rule violation eligible for strict evaluation that went undetected.
- **False Positive (FP)**: Spurious rule violation detected on clean negative controls.
- **True Negative (TN)**: Clean negative control producing zero false violations.
- **Precision**: $\frac{TP}{TP + FP}$
- **Recall**: $\frac{TP}{TP + FN}$
- **F1 Score**: $\frac{2 \times P \times R}{P + R}$

### 3. Duplicate Sensitivity (P3)
- Evaluated descriptively via Channel B shift. Reported as `DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE`.

### 4. Clean Negative Control FPR (P9)
- Proportion of unperturbed clean contracts that trigger false positive repair recommendations or rule violations.
