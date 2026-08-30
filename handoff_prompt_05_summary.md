# Prompt 5: Discourse Coherence Model & Registry Summary

RESEARCH/DEMO PROJECT — per Global Execution Contract, all metrics below are real measured results from runs executed in this session and preserved in documented fixtures.

---

## 1. What Was Built

1. **Consecutive-Clause Pair Constructor (`src/coherence/pair_sampler.py`):**
   - Implemented `CoherencePairSampler` generating labeled training/eval pairs from legal documents.
   - **Positive pairs (label=1.0):** Consecutive clause transitions $(c_i, c_{i+1})$ representing legitimate sequential discourse flow.
   - **Hard negative pairs (label=0.0):** Same-document non-consecutive jumps $(c_i, c_{i+k})$ ($k \ge 2$) and reversed clauses $(c_{i+1}, c_i)$.
   - **Easy negative pairs (label=0.0):** Cross-document clause pairs $(c_i^{\text{Doc } A}, c_j^{\text{Doc } B})$.
   - Configurable sampling ratio (default 1.0 : 1.0 : 1.0).

2. **PyTorch Neural Coherence Scorer Head (`src/coherence/model.py`):**
   - Designed `CoherenceScorerHead` operating over Legal-BERT clause embedding pairs $(u, v) \in \mathbb{R}^{768}$.
   - Rich feature extraction: $[u, v, |u - v|, u \odot v] \in \mathbb{R}^{3072}$.
   - MLP classification layers: `Linear(3072, 256) -> LayerNorm -> ReLU -> Dropout(0.2) -> Linear(256, 64) -> ReLU -> Dropout(0.1) -> Linear(64, 1)`.
   - Probability calibration helper returning continuous scores $\in [0.0, 1.0]$.

3. **Training & Curve Recording Pipeline (`src/coherence/trainer.py`):**
   - Utilizes cached 768-dim Legal-BERT embeddings from Prompt 4 (zero duplicate computation).
   - Trained with `AdamW` and `BCEWithLogitsLoss`.
   - Logs real epoch-by-epoch loss, accuracy, precision, recall, F1, and ROC-AUC.
   - Saves model checkpoint to `models/coherence_classifier.pt` and metrics fixture to `fixtures/coherence_training_curves.json`.

4. **Zero-Shot LLM Alternative Path (`src/coherence/zero_shot.py`):**
   - Implemented `ZeroShotCoherenceModel` using local open-source NLI / semantic continuity scoring.
   - 100% local execution with zero paid API dependencies (compliant with Contract §6).

5. **Unified Model Registry (`src/coherence/factory.py`):**
   - Standardized `CoherenceModelInterface` consumed by downstream Prompt 6 dual-channel scoring.
   - Switchable via `get_coherence_model("fine_tuned")` or `get_coherence_model("zero_shot")`.

---

## 2. Acceptance Gates Verification

| Gate | Requirement | Verification Script | Status | Measured Result |
|---|---|---|---|---|
| **Gate 1** | Pair construction on full document with sane easy/hard counts | `verify_pair_sampling.py` | **PASS** | $25$ pos, $25$ hard neg, $25$ easy neg on sample contract ($1:1:1$ ratio) |
| **Gate 2** | Fine-tuned model trains without crashing with real stored curves | `train_coherence_model.py` | **PASS** | 12 epochs on 894 pairs; final val loss $0.8856$, val acc $0.6236$, val ROC-AUC $0.6446$ |
| **Gate 3** | Zero-shot path runs end-to-end and returns scores in $[0, 1]$ | `demo_coherence_registry.py` | **PASS** | Coherent score: $0.8703$, range verified $[0.0, 1.0]$ |
| **Gate 4** | Both paths swappable via model registry | `gate_validation_prompt_05.py` | **PASS** | Verified identical `score_pair` interface across both engines |

---

## 3. Real Training & Validation Metrics (Provenance: `fixtures/coherence_training_curves.json`)

| Epoch | Train Loss | Val Loss | Val Accuracy | Val Precision | Val Recall | Val F1 | Val ROC-AUC |
|---|---|---|---|---|---|---|---|
| 1 | 0.647443 | 0.620028 | 0.6854 | 0.0000 | 0.0000 | 0.0000 | 0.5205 |
| 2 | 0.639765 | 0.627090 | 0.6854 | 0.0000 | 0.0000 | 0.0000 | 0.5429 |
| 3 | 0.626880 | 0.618818 | 0.6854 | 0.0000 | 0.0000 | 0.0000 | 0.5422 |
| 4 | 0.614028 | 0.617255 | 0.6854 | 0.5000 | 0.0179 | 0.0345 | 0.5764 |
| 5 | 0.568292 | 0.659927 | 0.6348 | 0.4308 | 0.5000 | 0.4628 | 0.5934 |
| 6 | 0.558121 | 0.641362 | 0.6629 | 0.2500 | 0.0357 | 0.0625 | 0.6127 |
| 7 | 0.510774 | 0.657054 | 0.6124 | 0.1905 | 0.0714 | 0.1039 | 0.6408 |
| 8 | 0.429119 | 0.706326 | 0.6124 | 0.4085 | 0.5179 | 0.4567 | 0.6221 |
| 9 | 0.396780 | 0.738203 | 0.6124 | 0.3415 | 0.2500 | 0.2887 | 0.6367 |
| 10 | 0.362152 | 0.775517 | 0.5955 | 0.2778 | 0.1786 | 0.2174 | 0.6350 |
| 11 | 0.327901 | 0.833083 | 0.6011 | 0.2857 | 0.1786 | 0.2198 | 0.6408 |
| 12 | 0.339695 | 0.885600 | 0.6236 | 0.3721 | 0.2857 | 0.3232 | 0.6446 |

- **Model Checkpoint:** `models/coherence_classifier.pt` ($3,218,396$ bytes)
- **All Pytest Tests:** 23/23 passing ($100\%$ pass rate across entire codebase).

---

## 4. Starting Point for Prompt 6

Prompt 6 (Dual-Channel Scoring & Discontinuity Detection) can consume Channel B directly:

```python
from src.coherence.factory import get_coherence_model

# Retrieves the active coherence model ("fine_tuned" or "zero_shot")
coherence_scorer = get_coherence_model()

# Score transition between two consecutive clauses
transition_score = coherence_scorer.score_pair(clause_a, clause_b)
```
