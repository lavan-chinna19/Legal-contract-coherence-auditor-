# Candidate Comparison Report

## Test Partition Model Comparison
- B0 Channel B: High sensitivity, 100% false positive rate on negative controls.
- B1 Dual Channel: Fails to suppress false positives on real contracts.
- B2 Cosine Distance: 38% specificity, 100% recall.
- C1 Boundary Contrast: 0% specificity on real SEC contracts.
- C2 Sequence BiLSTM: Historically reported as 0% recall (underfitting); note that in raw stored predictions (case_level_predictions.csv) uncalibrated scores (~0.523) crossed threshold 0.50 yielding TP=2, FP=16, FN=0, TN=0. Reconciled in Phase 4D-C-A audit.
- C3 Topological DAG: 100% recall, but 69% false positive rate (11/16 FP) on valid contracts.
