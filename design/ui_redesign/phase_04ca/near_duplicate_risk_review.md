# LexAudit Phase 4C-A — Near-Duplicate & Cross-Split Similarity Review

## 1. Methodology
Every held-out test contract was cross-compared against all 12 training-seen contracts using:
- **Exact SHA-256 byte hash equality**
- **Normalized text hash equality** (lowercased alphanumeric collapse)
- **5-gram token Jaccard similarity** to identify structural boilerplate reuse
- **SEC CIK / Registrant metadata analysis**

## 2. Key Audit Findings
- **Exact Raw Byte Duplicates**: 0 (Zero exact file matches between train and test splits).
- **Normalized Text Duplicates**: 0 (Zero normalized matches).
- **Max Observed 5-gram Jaccard Similarity**: 0.5272.
- **Shared Registrant CIKs**: Several documents share CIK prefix `0001558370` because they represent different Exhibit 10 attachments filed under the same quarterly report.

## 3. Benchmark Evaluation Cases Audit
Examining the 9 held-out contracts actually used in the Phase 4C synthetic displacement benchmark:

| Evaluation Doc ID | Clauses | Most Similar Train Doc | Max 5-gram Jaccard | Shared CIK? | Risk Classification |
| :--- | :---: | :--- | :---: | :---: | :--- |
| `0001493152_23_045259_EX-10_14` | 28 | `0001493152_23_045259_EX-10_12` | 0.1108 | True | SAME_CIK_DIFFERENT_CONTRACT |
| `0001558370_23_019889_EX-10_41` | 6 | `0000737758_23_000034_EX-10_29` | 0.0071 | False | VERIFIED_DISJOINT |
| `0001558370_23_019889_EX-10_42` | 9 | `0001477932_23_009214_EX-10_17` | 0.0086 | False | VERIFIED_DISJOINT |
| `0001558370_23_019889_EX-10_43` | 17 | `0001477932_23_009244_EX-10_9` | 0.0104 | False | VERIFIED_DISJOINT |
| `0001558370_23_019892_EX-10_88` | 13 | `0001437749_23_035505_EX-10_214` | 0.0087 | False | VERIFIED_DISJOINT |
| `0001558370_23_020000_EX-10_26` | 15 | `0001493152_23_045259_EX-10_12` | 0.0071 | False | VERIFIED_DISJOINT |
| `0001558370_23_020000_EX-10_30` | 19 | `0001477932_23_009244_EX-10_9` | 0.0153 | False | VERIFIED_DISJOINT |
| `0001802974_23_000037_EX-10_18` | 5 | `0000867773_23_000117_EX-10_12` | 0.0236 | False | VERIFIED_DISJOINT |
| `0001802974_23_000037_EX-10_24` | 15 | `0001493152_23_045259_EX-10_12` | 0.0037 | False | VERIFIED_DISJOINT |

## 4. Academic Rigor Assessment
While contracts represent independent legal transactions (commercial agreements, lease amendments, master services agreements), shared boilerplate clauses (governing law, entire agreement) yield baseline non-zero Jaccard similarities (0.05 to 0.25), typical of standardized legal drafting.
Zero exact document leaks or near-verbatim clones exist.
