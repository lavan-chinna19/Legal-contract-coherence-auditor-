# LexAudit Phase 4C — Abstention Criteria and Empirical Threshold Validation

## 1. Rationale and Philosophy of Abstention

In high-stakes legal document review, a false recommendation (suggesting moving a clause when its placement is legally sound or when evidence is ambiguous) is far more damaging than silence. Therefore, the system adheres to a strict principle:
> **A higher-ranked alternative position is NOT automatically a recommendation. The system must explicitly abstain when empirical evidence is insufficient or ambiguous.**

---

## 2. Critique and Correction of Phase 4A Threshold Proposal

In Phase 4A, an unvalidated heuristic threshold of $\Delta J > 0.15$ was informally suggested.

### Why $\Delta J > 0.15$ Was Scientifically Flawed:
The primary objective $J(D)$ is the **mean** combined anomaly across all $N$ clauses. Relocating a single clause affects at most three adjacent transitions out of $N-1$ transitions.
For a typical 15-clause agreement ($N=15$), each transition contributes approximately $\frac{1}{15} \approx 0.0667$ of the document score. Even if moving a clause changes an edge anomaly from $0.80$ to $0.20$ ($\Delta A = 0.60$), the overall document mean anomaly shifts by:
$$\Delta J \approx \frac{0.60 \times 0.5}{15} = 0.020$$
Requiring $\Delta J > 0.15$ would demand a document-level anomaly reduction that is mathematically impossible for single-clause relocation in documents of realistic length ($N \ge 8$), resulting in a near-100% false-negative rate!

---

## 3. Empirically Grounded Decision Policy

Using calibration data on development contract splits (completely separate from the held-out test set), an empirical threshold was pre-registered:
$$\tau_{\text{abstain}} = 0.0050 \quad (\text{0.50\% absolute document anomaly reduction})$$
$$\epsilon_{\text{tie}} = 0.0001 \quad (\text{numerical tie resolution})$$

### Formal Decision Tree:
```mermaid
graph TD
    Start[Evaluate all N candidate positions] --> CheckOriginal{Is Original Slot Rank 1?}
    CheckOriginal -- Yes --> Abstain1[ABSTAIN: ORIGINAL_POSITION_ALREADY_OPTIMAL]
    CheckOriginal -- No --> CheckImprovement{Is Delta J of Best Candidate > 0?}
    CheckImprovement -- No --> Abstain2[ABSTAIN: NO_IMPROVEMENT_OVER_ORIGINAL]
    CheckImprovement -- Yes --> CheckThreshold{Is Delta J >= 0.0050?}
    CheckThreshold -- No --> Abstain3[ABSTAIN: IMPROVEMENT_BELOW_THRESHOLD]
    CheckThreshold -- Yes --> CheckTie{Is |J_1 - J_2| <= 0.0001?}
    CheckTie -- Yes --> Abstain4[ABSTAIN: MULTI_CANDIDATE_OBJECTIVE_TIE]
    CheckTie -- No --> Recommend[RECOMMEND: Suggest Position with Human Review Caveat]
```

---

## 4. Empirical Negative Control Validation

To verify that the system does not hallucinate repairs on correctly drafted agreements, 9 pristine, unperturbed commercial contracts from the held-out SEC EDGAR test set were tested.

### Negative Control Results

| Document ID | Clauses ($N$) | Target Clause | Abstention Status | Detailed Reason | Recommended Move? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0001493152_23_045259_EX-10_14` | 28 | `..._14_14` | **ABSTAIN** | `MULTI_CANDIDATE_OBJECTIVE_TIE` | **No (False Alarm Prevented)** |
| `0001558370_23_019889_EX-10_41` | 6 | `..._41_3` | **ABSTAIN** | `NO_IMPROVEMENT_OVER_ORIGINAL` | **No (False Alarm Prevented)** |
| `0001558370_23_019889_EX-10_42` | 9 | `..._42_4` | **ABSTAIN** | `IMPROVEMENT_BELOW_THRESHOLD (delta=0.0013 < 0.0050)` | **No (False Alarm Prevented)** |
| `0001558370_23_019889_EX-10_43` | 17 | `..._43_8` | **ABSTAIN** | `IMPROVEMENT_BELOW_THRESHOLD (delta=0.0003 < 0.0050)` | **No (False Alarm Prevented)** |
| `0001558370_23_019892_EX-10_88` | 13 | `..._88_6` | **ABSTAIN** | `IMPROVEMENT_BELOW_THRESHOLD (delta=0.0004 < 0.0050)` | **No (False Alarm Prevented)** |
| `0001558370_23_020000_EX-10_26` | 15 | `..._26_7` | **ABSTAIN** | `IMPROVEMENT_BELOW_THRESHOLD (delta=0.0010 < 0.0050)` | **No (False Alarm Prevented)** |
| `0001558370_23_020000_EX-10_30` | 19 | `..._30_9` | **ABSTAIN** | `IMPROVEMENT_BELOW_THRESHOLD (delta=0.0003 < 0.0050)` | **No (False Alarm Prevented)** |
| `0001802974_23_000037_EX-10_18` | 5 | `..._18_2` | **ABSTAIN** | `ORIGINAL_POSITION_ALREADY_OPTIMAL` | **No (False Alarm Prevented)** |
| `0001802974_23_000037_EX-10_24` | 15 | `..._24_7` | **ABSTAIN** | `ORIGINAL_POSITION_ALREADY_OPTIMAL` | **No (False Alarm Prevented)** |

### Summary Metrics:
- **Total Clean Negative Controls**: 9
- **Abstention Rate**: **100.0%** (9/9)
- **False Repair Rate**: **0.00%** (0/9)
- **Sensitivity Threshold Safety**: The calibrated $\tau = 0.0050$ successfully filtered out 5 instances where trivial noise ($\Delta J < 0.0015$) would have triggered spurious recommendations.
