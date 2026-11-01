# LexAudit Research — Reference vs. Optimized Rescoring Parity
<!-- Reference copy for research archive -->

## 1. Parity Requirement
$|J_{\text{optimized}} - J_{\text{reference}}| \le 10^{-6}$ for all candidate permutations.

## 2. Parity Test Results
- Document Scenarios: 8 structural permutations (Middle, Start-to-End, End-to-Start, Adjacent Forward, Adjacent Backward, $N=2$ Swap, Identical Bodies, Identity).
- Measured Max Discrepancy: `0.00000000` (exact 8-decimal float equivalence).
- Mean Discrepancy: `0.00000000`.
- Parity Status: **CONFIRMED PASS**.

## 3. Scaling Profile
- $N=5$: 22.1 ms (Ref) vs 3.2 ms (Opt) -> 6.9x speedup.
- $N=10$: 94.2 ms (Ref) vs 6.8 ms (Opt) -> 13.9x speedup.
- $N=20$: 272.6 ms (Ref) vs 12.8 ms (Opt) -> 21.3x speedup.
Optimized implementation enables real-time interactive decision support.
