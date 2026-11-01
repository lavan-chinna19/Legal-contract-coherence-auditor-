# Failure Mode Review
- Semantic models (B0, B1, C1) fail on negative controls due to high normal transition variance in SEC contracts.
- Heuristic models (C3) fail on negative controls due to assuming all contracts adhere to canonical heading sequence.
- BiLSTM (C2) historically reported as underfitting (0% recall); raw predictions yielded universal positives due to uncalibrated sigmoid output exceeding 0.50 threshold (see Phase 4D-C-A audit).
