# Channel B Response and Structural Failure Root Cause Review

**Document ID**: `PHASE_04DA_ROOT_CAUSE_REVIEW`  
**Auditor**: Principal ML Research Auditor & Legal NLP Scientist  
**Scope**: Empirical Boundary Analysis, Logit Saturation, and Systematic Hypothesis Classification  

---

## 1. Executive Summary

Phase 4D reported that Channel B failed to detect 6 out of 6 structural perturbations (0.0% detection rate). This audit investigated the underlying neural compatibility scores, pairwise boundary edges, aggregation functions, and evaluation definitions.

The analysis reveals that **the failure is multi-causal**, stemming from both model-level limitations (logit saturation and narrow dynamic range) and evaluation-level defects (misconceived threshold and dilution). 

---

## 2. Empirical Transition Boundary Evidence

From [`design/ui_redesign/phase_04da/channel_b_boundary_analysis.csv`](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04da/channel_b_boundary_analysis.csv), which tracked all 60 transition edges across the 6 structural scenarios:

1. **Compressed Transition Probability Band**:
   - Natural, standard adjacent pairs: $P \in [0.3102, 0.3389]$ (Anomaly $\alpha \in [0.6611, 0.6898]$).
   - Injected, perturbed adjacent pairs: $P \in [0.3120, 0.3266]$ (Anomaly $\alpha \in [0.6734, 0.6880]$).
   - **Total Probability Range Across All Edges**: $\Delta P_{\text{max}} = 0.0287$ ($2.87\%$).
2. **Per-Clause Maximum Channel B Shifts**:
   - Maximum observed positive shift: $+0.0152$ (`SCEN_P2_01_SWAP_ADJACENT` on `SYNTH_DOC_01_MSA_c00`).
   - Maximum observed negative shift: $-0.0096$ (`SCEN_P1_01_DISP_DISTANT` on `SYNTH_DOC_01_MSA_c01`).
   - Mean absolute shift across all affected clauses: $0.0061$.

---

## 3. Systematic Hypothesis Classification

Each potential contributing factor identified during the audit was evaluated against empirical evidence:

### 1. Narrow Neural Compatibility Score Range
- **Classification**: **`VERIFIED ROOT CAUSE`**
- **Evidence**: The fine-tuned Legal-BERT coherence classifier outputs transition probabilities tightly clustered between $0.3102$ and $0.3389$ across all pairs. The model lacks dynamic range resolution; unnatural transitions (e.g., Exhibit A $\to$ Scope of Services) produce probabilities virtually indistinguishable from natural transitions (Preamble $\to$ Scope).

### 2. Channel A Dilution in Combined Scoring
- **Classification**: **`VERIFIED ROOT CAUSE`**
- **Evidence**: Combined score $S = 0.5 A + 0.5 B$. For standard contract clauses, $A = 0.0000$. This halves the impact of any transition disruption ($0.5 \times 0.0152 = +0.0076$). To reach the $0.50$ Medium severity threshold, $B$ would have to increase by $+0.3200$, which is physically impossible given the model's $0.0287$ total spread.

### 3. Severity Classification Threshold Effects
- **Classification**: **`VERIFIED ROOT CAUSE`**
- **Evidence**: Production severity requires composite $S \ge 0.50$ or single-channel breach $\ge 0.70$. Baseline synthetic contracts have $S \approx 0.3400$ (`CLEAN` tier, cutoff $0.35$). The maximum perturbation shifted $S$ to $0.3440$ and single-channel $B$ to $0.6880$. Both remain below their respective thresholds ($0.3440 < 0.3500$ and $0.6880 < 0.7000$), resulting in $0$ production anomaly flags.

### 4. Incorrect Evaluation Benchmark Definition (Phase 4D)
- **Classification**: **`VERIFIED ROOT CAUSE`**
- **Evidence**: Phase 4D evaluated structural detection by inventing an ad-hoc runner parameter (`structural_anomaly_threshold = 0.08`) applied to $\Delta S_B$, while falsely describing it as "the production anomaly threshold". Because $\Delta S_B \le 0.0152$, it declared 0/6 detection while failing to examine whether production anomaly thresholds were even triggered or why the model dynamic range was compressed.

### 5. Pairwise Model Saturation / Lack of Discriminating Signal
- **Classification**: **`SUPPORTED HYPOTHESIS`**
- **Evidence**: Because the coherence model was trained on pairwise next-sentence/next-clause objectives where both classes shared high lexical similarity, the classifier's output layer produces logits with very low variance on unseen synthetic formal contract prose.

### 6. Ambiguous Legal Clause Order (Boilerplate Permutations)
- **Classification**: **`SUPPORTED HYPOTHESIS`**
- **Evidence**: In `SCEN_P2_03_SWAP_SUBTLE`, Section 5 (Confidentiality) and Section 7 (Indemnification) were swapped. In commercial contract drafting, the relative ordering of standard boilerplate risk-allocation clauses is legally interchangeable. Neither order represents a defective contract. Declaring this a "detection failure" reflects ambiguous ground truth rather than detector inaccuracy.

### 7. Score Aggregation Masking Local Change
- **Classification**: **`SUPPORTED HYPOTHESIS`**
- **Evidence**: Channel B aggregates clause score as $B_i = \max(\alpha_{\text{in}}, \alpha_{\text{out}})$. If a perturbation causes $\alpha_{\text{out}}$ to rise from $0.6728$ to $0.6780$, but $\alpha_{\text{in}}$ was already $0.6842$, the clause score remains $0.6842$, masking the transition shift.

### 8. Training-Label Mismatch / Domain Shift
- **Classification**: **`UNVERIFIED HYPOTHESIS`**
- **Evidence**: While the training data split was derived from EDGAR Form 10-K exhibits, synthetic contracts use shorter, simplified clauses. Whether domain shift explains logit compression cannot be verified without retraining (which is strictly prohibited in Phase 4D-A).

### 9. Software Arithmetic / Implementation Bug
- **Classification**: **`RULED OUT`**
- **Evidence**: All formulas for $S_A, S_B, S$, cosine distance, pair scoring, and severity assessment were independently implemented and matched code outputs to machine precision ($0.0000$ error). No arithmetic bug exists.

---

## 4. Remediation Recommendations for Future Research Phases

1. **Dynamic Logit Calibration (Future Phase)**: Apply temperature scaling or post-hoc Platt scaling to expand the effective dynamic range of the coherence model logits.
2. **Clause-Level Sequence Modeling**: Replace independent pairwise classification with a global document sequence encoder (e.g., hierarchical transformer or Longformer) that considers full contract topology.
3. **Decoupled Structural Scoring**: Evaluate structural coherence separately from semantic OOD rather than combining them via an unweighted average that dilutes transition breaks.
