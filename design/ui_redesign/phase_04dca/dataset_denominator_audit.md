# Dataset Denominator & Partition Reconciliation Audit

**Audit Program**: LexAudit Data Integrity & Denominator Reconciliation (Phase 4D-C-A)  
**Investigation Scope**: Audit C — Resolution of SEC Source Inventory & 32 vs 31 Parent Agreement Discrepancy  
**Auditor**: Data Integrity Engineer, Senior Python Testing Engineer  
**Status**: **RECONCILED & MATHEMATICALLY VERIFIED**

---

## 1. Resolution of the 32 vs 31 Discrepancy

### The Problem
The Phase 4D-C summary report narrative stated:
> "32 independent parent agreements across 15 corporate entity families: Development: 19 parent contracts. Validation: 7 parent contracts. Test: 5 parent contracts."

However:
$$19 + 7 + 5 = 31 \neq 32$$

### The Forensic Finding
Direct recalculation from the authoritative machine-readable manifest (`parent_contract_manifest.csv`) and family split allocation manifest (`source_family_split_manifest.csv`) revealed that **the underlying data manifests were completely correct and mathematically consistent**. The error was purely a **narrative typographical error in report writing**.

The true authoritative numbers are:
$$\mathbf{Development:\text{ }18\text{ parents (9 families)}}$$
$$\mathbf{Validation:\text{ }9\text{ parents (3 families)}}$$
$$\mathbf{Sealed\text{ }Test:\text{ }5\text{ parents (3 families)}}$$
$$\mathbf{Total:\text{ }18 + 9 + 5 = 32\text{ parents across 15 families}}$$

The report author mistakenly transposed numbers from an earlier draft, writing "19" instead of "18" and "7" instead of "9".

---

## 2. Exhaustive SEC EDGAR Source Inventory & Manifest Verification

### Dissection of `edgar_manifest.json`
An audit of `data/raw/sec_edgar/edgar_manifest.json` investigated an earlier confusing reference to "10 filings":
1. **Root Cause**: The JSON file is structured as a single top-level dictionary containing **10 metadata keys**:
   `['generated_at', 'strategy', 'efts_note', 'target_count', 'candidates_checked', 'skipped_no_ex10', 'manifest_count', 'fetched_count', 'failed_count', 'entries']`.
   An earlier auditor took `len(data)` and mistakenly assumed the integer 10 represented "10 Form 10-K filings".
2. **True Inventory Counts**:
   Inspecting the `manifest["entries"]` array reveals:
   - **Total Exhibit Entries**: Exactly **50 exhibit records** (`entries`).
   - **Unique Accession Numbers**: Exactly **19 unique SEC accession numbers** (`accession_no`).
   - **Unique CIKs**: Exactly **19 distinct corporate entities** (`cik`).
   - **Downloaded Physical Files**: Exactly **50 `.txt` files** located in `data/raw/sec_edgar/`.
   - **Size-Filtered Exclusions**: **18 raw exhibits** excluded due to clause bounds ($<10$ or $>125$ clauses).
   - **Eligible Independent Parent Agreements**: Exactly **32 parent agreements** ($50 - 18 = 32$).
   - **Eligible Corporate Entity Families**: Exactly **15 corporate entity families** (4 CIKs in the raw pool had all exhibits filtered out or grouped).

| Dataset Inventory Metric | Authoritative Count | Authoritative Source File | Invariant / Validation Status |
| :--- | :---: | :--- | :---: |
| **Manifest Top-Level Keys** | **10** | `data/raw/sec_edgar/edgar_manifest.json` | Metadata keys; NOT filing count. |
| **Total Exhibit Entries in Manifest** | **50** | `edgar_manifest.json["entries"]` | 50 exhibit entries verified. |
| **Unique SEC Accession Numbers** | **19** | `edgar_manifest.json` (`accession_no`) | 19 unique filings from which exhibits were drawn. |
| **Unique CIKs in Raw Manifest** | **19** | `edgar_manifest.json` (`cik`) | 19 unique registrant corporate entities. |
| **Total Downloaded Exhibit Text Files** | **50** | `data/raw/sec_edgar/*.txt` | 50 physical text files in local storage. |
| **Raw Exhibits Excluded (<10 or >125 clauses)** | **18** | `src/research/independent_benchmark/provenance.py` | Excluded by pilot size bounds. |
| **Eligible Independent Parent Agreements** | **32** | `parent_contract_manifest.csv` | All 32 pass segmentation filters. |
| **Distinct Corporate Entity Families (Parents)** | **15** | `source_family_split_manifest.csv` | Grouped by unique CIK. |
| **Unique Parent Document IDs** | **32** | `parent_contract_manifest.csv` | 100% unique primary keys. |
| **Unique Source Text SHA-256 Hashes** | **32** | `parent_contract_manifest.csv` | 0 duplicate source documents. |
| **Cross-Split Near-Duplicate Pairs** | **0** | `duplicate_and_near_duplicate_audit.csv` | Jaccard similarity $< 0.85$ across splits. |

---

## 3. Partition and Case Counts Reconciliation

```text
========================================================================================
SPLIT PARTITION      FAMILIES   PARENTS   TOTAL CASES   ELIGIBLE CASES   EXCLUDED (AMBIG)
========================================================================================
Development                 9        18           106               88                 18
Validation                  3         9            45               36                  9
Sealed Test                 3         5            23               18                  5
----------------------------------------------------------------------------------------
TOTAL                      15        32           174              142                 32
========================================================================================
```

### Breakdown of the 23 Test Cases (Sealed Test Split):
- **18 Eligible Cases**:
  - **2 Positive Cases** (Category P1 & P2, both from single parent `SEC_CIK932021_EX_10_26`)
  - **5 N1 Clean Controls** (Canonical contract structure from 5 distinct parents)
  - **3 N2 Covenant Swaps** (Boilerplate section swaps)
  - **5 N3 Dispute Front-Loaded** (Alternative commercial drafting variation)
  - **3 N4 Definitions Front-Loaded** (Alternative commercial drafting variation)
- **5 Excluded Ambiguous Cases**:
  - Category A1 (Clause swaps resulting in indeterminate coherence)

---

## 4. Split Isolation and Disjointness Proofs

Automated regression assertions in `tests/test_phase_04dca_audit.py` guarantee:
1. **Family Disjointness**: Every corporate entity family (CIK) appears in strictly one split partition ($Dev \cap Val = \emptyset$, $Dev \cap Test = \emptyset$, $Val \cap Test = \emptyset$).
2. **Child Case Containment**: Every child perturbation case strictly inherits the split assignment of its parent contract.
3. **No Leakage**: Zero text overlap, duplicate text, or vocabulary leakage across splits.
