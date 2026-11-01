# Final Independent Contract Benchmark Report (Phase 4D-C)

## Executive Summary
Phase 4D-C constructed and evaluated an independent, leakage-free legal contract structural coherence benchmark using 32 real SEC EDGAR material contracts across 15 distinct corporate entity families.

## Test Set Evaluation Results
| Model Key | Architecture | Cases | TP | FP | FN | TN | Recall (95% CI) | Specificity (95% CI) | F1 | Balanced Acc |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| B0_ChannelB | B0_ChannelB | 18 | 2 | 16 | 0 | 0 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.20 | 0.50 |
| B1_ProductionEnsemble | B1_ProductionEnsemble | 18 | 2 | 16 | 0 | 0 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.20 | 0.50 |
| B2_CosineSimilarity | B2_CosineSimilarity | 18 | 2 | 10 | 0 | 6 | 1.00 [0.3424, 1.0] | 0.38 [0.1848, 0.6136] | 0.29 | 0.69 |
| C1_BoundaryContrast | C1_BoundaryContrast | 18 | 2 | 16 | 0 | 0 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.20 | 0.50 |
| C2_SequenceBiLSTM | C2_SequenceBiLSTM | 18 | 2 | 16 | 0 | 0 | 1.00 [0.3424, 1.0] | 0.00 [0.0, 0.1936] | 0.20 | 0.50 |
| C3_TopologicalDAG | C3_TopologicalDAG | 18 | 2 | 11 | 0 | 5 | 1.00 [0.3424, 1.0] | 0.31 [0.1416, 0.556] | 0.27 | 0.66 |
