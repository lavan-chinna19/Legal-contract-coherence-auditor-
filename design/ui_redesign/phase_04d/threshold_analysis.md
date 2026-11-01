# Phase 4D Threshold Sensitivity and Calibration Analysis

## 1. Threshold Independence Discipline
In accordance with Contract §14, all existing production and experimental thresholds were held strictly frozen:
- **Production Anomaly Threshold**: $\tau_{\text{prod}} = 0.0800$ (Unchanged)
- **Experimental Abstention Threshold**: $\epsilon = 0.0050$ (Unchanged)
- **Rule Violation Weights**: $\omega_{\text{rules}} = 1.0000$ (Unchanged)

## 2. Offline Threshold Grid Sensitivity
An offline threshold sweep ($\tau \in [0.02, 0.15]$) was conducted across the 6 canonical structural perturbation scenarios (P1 and P2):
- At $\tau = 0.0800$, structural detection rate is **0.0%**.
- Even lowering $\tau$ to $0.0200$ yields **0.0%** thresholded anomaly count increase on single clause displacements.
- **Root Cause**: The Channel B anomaly threshold applies to the *absolute* pair anomaly score $S_B(c_i, c_{i+1})$, rather than the relative differential $\Delta S_B$. For well-formed legal drafting sequences, even an unexpected clause pair maintains a relatively low absolute anomaly score compared to synthetically scrambled noise sequences used during calibration.
- **Recommendation**: Future phases should explore relative boundary shift detectors ($\Delta S_B > k \cdot \sigma$) rather than relying purely on static absolute cutoffs for single clause displacements.
