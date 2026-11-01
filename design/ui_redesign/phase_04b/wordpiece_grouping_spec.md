# Phase 4B — WordPiece Subword Grouping Specification & Validation

**Project:** Legal Contract Coherence Auditor (LexAudit)  
**Phase:** 4B — Professional Explainability Workspace  
**Date:** 2026-10-14  
**Author:** Principal NLP Research Engineer & Senior Next.js/React Architect  
**Status:** PASS — 12/12 UNIT TESTS PASSED  

---

## 1. Motivation & Interpretability Problem

Legal-BERT's WordPiece tokenizer frequently breaks complex legal terms into fragmented subwords:
- Example: `["indem", "##nifi", "##cation"]` $\to$ *indemnification*
- Example: `["sever", "##ability"]` $\to$ *severability*

Presenting raw WordPiece fragments directly to legal reviewers creates cognitive friction. However, aggregating attributions naively risks obscuring which specific morpheme or character sequence drove the model's prediction.

---

## 2. Mathematical Grouping Specification

The subword reconstruction algorithm is implemented in `frontend/src/components/explainability/wordpieceGrouping.ts`:

### A. Subword Attachment Rule
A token $t_i$ belongs to the current word group if:
1. It begins with the prefix marker `##` (indicating a continuation WordPiece).
2. The current group does not represent a special token (`[CLS]`, `[SEP]`, `[UNK]`).
3. The preceding token was not a standalone punctuation character.

When attached, the reconstructed word string is:
$$w = w \mathbin{\Vert} \text{strip\_prefix}(t_i, \text{"\#\#"})$$

### B. Attribution Aggregation Formulas
For a word group containing $K$ subwords with raw attributions $[a_1, a_2, \dots, a_K]$:
1. **Total Sum Attribution:**
   $$A_{\text{sum}} = \sum_{k=1}^K a_k$$
2. **Mean Attribution:**
   $$A_{\text{mean}} = \frac{1}{K}\sum_{k=1}^K a_k$$
3. **Peak Subtoken Attribution:**
   $$a^* = a_{\arg\max_k |a_k|}$$
   $$A_{\text{max}} = a^*$$
4. **Dominant Subtoken:**
   Identifies the specific subword contributing the largest absolute gradient magnitude to the prediction.

### C. Information Preservation Safeguards
- **Original Subtokens Preserved:** Clicking any grouped word chip in the UI immediately opens `TokenDetailPanel`, displaying every raw subword, its original token index, and its exact unaggregated attribution.
- **View Mode Switcher:** Reviewers can freely toggle between **Group Subwords (Readable)** and **Raw WordPiece Tokens** at any time.

---

## 3. Comprehensive Unit Test Coverage

Twelve automated test cases were authored and executed via `tests/test_wordpiece_grouping.py`:
1. `TC-01-Normal-Words`: Simple unfragmented words.
2. `TC-02-Split-Words`: Multi-part subwords (`indem` + `##nifi` + `##cation`).
3. `TC-03-Standalone-Punctuation`: Distinct periods, commas, semicolons.
4. `TC-04-Sentence-Boundaries`: End of sentence with immediate capitalization.
5. `TC-05-Special-Tokens`: `[CLS]`, `[SEP]`, `[PAD]`.
6. `TC-06-Unknown-Tokens`: `[UNK]` handling without deceptive text substitution.
7. `TC-07-Negative-Attributions`: Multiple negative anchor tokens.
8. `TC-08-Positive-Attributions`: Multiple positive anomaly driver tokens.
9. `TC-09-Mixed-Signs`: Mixed signs within a single fragmented word.
10. `TC-10-Zero-Attribution`: Tokens with zero gradient.
11. `TC-11-Empty-Array`: Safe null/empty handling.
12. `TC-12-Long-Sequence`: 256-token legal sequence with repeated terms.

**Result:** All 12 test cases PASSED. Detailed execution output is archived in `design/ui_redesign/phase_04b/wordpiece_grouping_test_results.json`.
