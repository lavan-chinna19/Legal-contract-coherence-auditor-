# SCIENTIFIC REPRODUCTION INSTRUCTIONS
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Environment:** Windows 11, Python 3.10+, PyTorch (CPU)

---

## 1. Quick Verification (All Baselines & Candidates)

To reproduce all evaluations across Diagnostic, Validation, and Held-Out Test partitions and generate all case-level predictions:

```bash
# From repository root:
python -m src.research.structural_coherence.evaluator
```

This generates:
- `research/structural_coherence_phase_04db/case_level_predictions.csv`
- `research/structural_coherence_phase_04db/evaluation_summary.json`

---

## 2. Model Training Reproduction (Candidate C2 BiLSTM)

To re-run the bounded CPU training of Candidate C2 (under 5 seconds):

```bash
python -m src.research.structural_coherence.training
```

Outputs:
- Checkpoint: `models/experimental/phase_04db/contextual_sequence_coherence.pt`
- Training history: `models/experimental/phase_04db/training_history.json`

---

## 3. Unit & Scientific Test Execution

To execute the complete research test suite verifying split isolation, label eligibility, and metric math:

```bash
python -m pytest tests/test_structural_coherence_model.py -v -ra
```

To run full backend regression:

```bash
python -m pytest tests/ -v -ra
```
