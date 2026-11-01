# LexAudit Phase 4A — Severity and Score Distribution Empirical Validation

## 1. Empirical Test Execution
- **Contract Fixture**: [fixture_01_baseline.txt](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_03a/fixtures/fixture_01_baseline.txt)
- **Document ID**: `doc_066a0456`
- **Total Clauses**: 5
- **Mean Anomaly Score**: `0.338`

---

## 2. Clause-by-Clause Verification Matrix

| Sequence | Clause ID | Combined Score ($S_i$) | Channel A Score ($S_A$) | Centroid Distance ($d$) | Nearest Centroid | Channel B Score ($S_B$) | Incoming Flow ($P_{in}$) | Outgoing Flow ($P_{out}$) | Assigned Severity |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **§ 0** | `doc_066a0456_0` | **0.312** | 0.285 | 0.2854 | `Term` | 0.339 | *First Clause* | 0.661 | **CLEAN** |
| **§ 1** | `doc_066a0456_1` | **0.345** | 0.310 | 0.3102 | `Confidentiality` | 0.380 | 0.661 | 0.579 | **CLEAN** |
| **§ 2** | `doc_066a0456_2` | **0.380** | 0.340 | 0.3398 | `Indemnification`| 0.420 | 0.579 | 0.580 | **CLEAN** |
| **§ 3** | `doc_066a0456_3` | **0.325** | 0.295 | 0.2947 | `Governing Law` | 0.355 | 0.580 | 0.710 | **CLEAN** |
| **§ 4** | `doc_066a0456_4` | **0.330** | 0.300 | 0.3001 | `Severability` | 0.360 | 0.710 | *Terminal Clause* | **CLEAN** |

### Mathematical Consistency Proofs
1. **Document Mean Score Consistency**:
   $$\bar{S} = \frac{0.312 + 0.345 + 0.380 + 0.325 + 0.330}{5} = \frac{1.692}{5} = 0.3384 \approx 0.338$$
   - Exactly matches the backend KPI: `0.338`.
2. **Severity Classification Consistency**:
   - High threshold $\tau_{high} = 0.65$: 0 clauses $\ge 0.65 \implies \text{High Count} = 0$.
   - Medium threshold $\tau_{med} = 0.40$: 0 clauses in $[0.40, 0.65) \implies \text{Medium Count} = 0$.
   - Low threshold $\tau_{low} = 0.40$: 0 clauses flagged.
   - Clean clauses: 5 clauses $< 0.40 \implies \text{Clean Count} = 5$ ($100.0\%$).
   - Sum: $0 + 0 + 0 + 5 = 5$ ($100.0\%$). Verified strictly conserved.
3. **Dual-Channel Weights**:
   - For all clauses, $S_i = 0.5 \cdot S_A + 0.5 \cdot S_B$.
   - For § 0: $0.5(0.285) + 0.5(0.339) = 0.1425 + 0.1695 = 0.3120$. Verified exact match.

---

## 3. UI Display Validation
During the CDP browser test execution ([run_phase4a_browser_verification.py](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/scripts/run_phase4a_browser_verification.py)):
- All 5 bars were rendered sequentially in authoritative numerical order (§ 0 to § 4).
- Bar heights reflected true combined score values.
- Hovering/clicking on § 2 updated the context strip to display: `Combined Score: 0.380`, `Channel A: 0.340`, `Channel B: 0.420`.
- The severity distribution table accurately reflected 0 High, 0 Medium, 0 Low, 5 Clean.
