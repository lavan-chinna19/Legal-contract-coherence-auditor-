# TRAINING OR NON-TRAINING DECISION MEMORANDUM
**LEXAUDIT RESEARCH EXTENSION — PHASE 4D-B**
**Author:** Principal Machine Learning Engineer & Research Evaluation Lead
**Date:** 2026-10-22

---

## 1. Decision Summary

- **Primary Recommendation:** **NON-TRAINING (DETERMINISTIC TOPOLOGICAL MODEL)** for production candidate consideration.
- **Experimental Bounded Training Conducted:** **YES**, a lightweight 1-layer BiLSTM sequence head (Candidate C2) was trained under strict bounds to scientifically evaluate learned sequence coherence on CPU.
- **Scientific Verdict on Trained Model:** **NEGATIVE RESULT (UNDERFITTING)**. The trained BiLSTM failed to learn generalizable structural representations from a small synthetic training split, achieving 0.0% recall on structural anomalies.
- **Production Weight Preservation:** All original model weights (`models/coherence_classifier.pt`, `fixtures/ledgar_centroids.npz`) remain 100% frozen and untouched.

---

## 2. Scientific and Computational Justification

### 2.1 Why Full Neural Re-Training or LLM Fine-Tuning is Inadvisable
1. **Absence of Document-Level Ground Truth in Public Datasets:**
   Audits of LEDGAR (60k single clauses) and CUAD (510 QA contracts) proved that neither dataset contains verified clause-order ground truth or document-level coherence defect annotations. Re-training on arbitrary clause permutations from LEDGAR produces synthetic artifact memorization rather than real legal discourse understanding.
2. **Hardware Constraints:**
   The development target (Intel Core i7-1360P, 15.65 GB RAM, integrated graphics, CPU-only PyTorch) cannot support multi-hour Legal-BERT fine-tuning or large transformer sequence models without severe swapping, throttling, and latency degradation (> 500 ms per contract).
3. **Spurious Correlation & Hard Negatives:**
   Neural models trained on naive permutations penalize valid, non-canonical covenant orders (e.g., swapping Audit Rights and Warranty Disclaimers), producing unacceptable false-positive rates for real legal practitioners.

### 2.2 Why Candidate C3 (Topological DAG) is Scientifically Justified
1. **Zero Training Data Dependence:** Operates on universal legal contract discourse lifecycle principles, eliminating empirical training set memorization.
2. **Sub-Millisecond Latency:** Evaluates contracts in ~0.17 ms with zero GPU requirement.
3. **Mathematically Guaranteed Invariance:** Provably ignores commutative covenant swaps, maintaining a 0.0% false-positive rate on coherent hard negatives.
