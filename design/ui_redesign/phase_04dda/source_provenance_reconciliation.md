# Phase 4D-D-A Source Provenance and Filer Identity Reconciliation
## SEC EDGAR Entity Verification, Contract Party Disambiguation, and Collision Prevention

### 1. Executive Summary of Provenance Corrections

During the Phase 4D-D audit, a severe discrepancy was discovered between narrative reporting labels and actual SEC EDGAR metadata:
- **8 out of 10 corporate registrant families** in Phase 4D-D narrative tables contained incorrect or placeholder entity names (e.g., CIK 810136 was mislabeled "Pioneer Natural Resources" instead of Photronics Inc., and CIK 932021 was mislabeled "Westlake Chemical" instead of Global Technologies Ltd.).
- While the underlying raw text files in `data/raw/sec_edgar/` and the original SEC metadata in `parent_contract_manifest.csv` were authentic SEC filings, the human narrative reports suffered from descriptive drift.
- In Phase 4D-D-A, 100% of parent contract filings have been re-anchored directly to their verified SEC EDGAR filing entity names, accession numbers, exhibit URLs, and cryptographic SHA-256 digests in [source_identity_corrections.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dda/source_identity_corrections.csv).

---

### 2. Systematic Filer Entity Reconciliation

The table below reconciles all 10 document families utilized across the benchmark:

| Document Family ID | SEC CIK | Phase 4D-D Reported Name (Erroneous/Drift) | Verified SEC EDGAR Entity Name | SEC Accession Number | Form / Exhibit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FAM_CIK_810136` | 0000810136 | Pioneer Natural Resources / Successor Entities | **PHOTRONICS INC (PLAB) (CIK 0000810136)** | `0001140361-23-059254` | 10-K / EX-10.12, 10.14, 10.15, 10.31 |
| `FAM_CIK_932021` | 0000932021 | Westlake Chemical Corp. | **GLOBAL TECHNOLOGIES LTD (GTLL) (CIK 0000932021)** | `0001493152-23-046428` | 10-K / EX-10.24, 10.26 |
| `FAM_CIK_808326` | 0000808326 | Emergent BioSolutions Inc. | **EMCORE CORP (EMKR) (CIK 0000808326)** | `0000808326-23-000031` | 10-K / EX-10.9 |
| `FAM_CIK_1967306` | 0001967306 | CleanSpark Inc. Related Entities | **Mercer Bancorp, Inc. (MSBB) (CIK 0001967306)** | `0001558370-23-020031` | 10-K / EX-10.9 |
| `FAM_CIK_1101396` | 0001101396 | Virgin Media / NTL Inc. | **DELTA APPAREL, INC (DLAPQ) (CIK 0001101396)** | `0001437749-23-035505` | 10-K / EX-10.27, 10.214 |
| `FAM_CIK_1397016` | 0001397016 | Bright Horizons Family Solutions | **Optex Systems Holdings Inc (OPXS) (CIK 0001397016)** | `0001493152-23-045259` | 10-K / EX-10.11, 10.12, 10.14, 10.15 |
| `FAM_CIK_1643988` | 0001643988 | Biohaven Pharmaceutical Holding | **Loop Media, Inc. (LPTV) (CIK 0001643988)** | `0001558370-23-019889` | 10-K / EX-10.40, 10.43 |
| `FAM_CIK_1802974` | 0001802974 | Snowflake Inc. Related Entities | **Mission Produce, Inc. (AVO) (CIK 0001802974)** | `0001802974-23-000037` | 10-K / EX-10.24 |
| `FAM_CIK_1090872` | 0001090872 | Agilent Technologies Inc. | **AGILENT TECHNOLOGIES, INC. (A) (CIK 0001090872)** | `0001090872-23-000020` | 10-K / EX-10.19, 10.20, 10.21, 10.22 |
| `FAM_CIK_1645590` | 0001645590 | Hewlett Packard Enterprise Co. | **Hewlett Packard Enterprise Co (HPE) (CIK 0001645590)** | `0001645590-23-000117` | 10-K / EX-10.35 |

---

### 3. Filer Registrant vs. Actual Contract Parties

A fundamental legal distinction required in legal NLP dataset engineering is separating the **SEC Filing Registrant** (the reporting company submitting Form 10-K) from the **Actual Contracting Parties** (the signatories named in the agreement). In commercial contracting:
1. **EX-10.15 (`SEC_CIK810136_EX_10_15`)**:
   - *Filing Registrant*: Photronics, Inc. (CIK 0000810136).
   - *Contract Agreement*: Technology License Agreement.
   - *Actual Contracting Parties*: Dai Nippon Printing Co., Ltd. (DNP) (Licensor) and Photronics, Inc. (Licensee).
2. **EX-10.31 (`SEC_CIK810136_EX_10_31`)**:
   - *Filing Registrant*: Photronics, Inc.
   - *Contract Agreement*: Master Outsource and Foundry Services Agreement.
   - *Actual Contracting Parties*: Photronics Singapore Pte. Ltd. and DNP Photomask Technology Taiwan Co., Ltd.
3. **EX-10.214 (`SEC_CIK1101396_EX_10_214`)**:
   - *Filing Registrant*: Delta Apparel, Inc. (CIK 0001101396).
   - *Contract Agreement*: Fourth Amended and Restated Credit Agreement.
   - *Actual Contracting Parties*: Delta Apparel, Inc., Salt Life, LLC, M.J. Soffe, LLC, as Borrowers, and Wells Fargo Bank, National Association, as Administrative Agent.
4. **EX-10.24 (`SEC_CIK932021_EX_10_24`)**:
   - *Filing Registrant*: Global Technologies Ltd. (CIK 0000932021).
   - *Contract Agreement*: Exclusive Licensing and Commercialization Agreement.
   - *Actual Contracting Parties*: Global Technologies Ltd. and TCGRx Holdings, LLC.

Documenting actual contracting parties prevents models from falsely assuming that every obligation in an exhibit is owed by or to the SEC filing registrant.

---

### 4. Provenance Mapping Invariants and Collision Prevention

#### The Substring Collision Flaw
In naive file loading implementations, matching files by substring using `f"CIK{cik}" in pid and ex_norm in pid` introduces a critical vulnerability:
- If an accession contains exhibit `EX-10.1` and exhibit `EX-10.12`, the normalized string for `EX-10.1` (`EX_10_1`) is an exact prefix substring of `EX_10_12` (`"EX_10_1" in "EX_10_12"` evaluates to `True`).
- If `EX-10.1` precedes `EX-10.12` in the manifest entries array, a naive `break` on substring match will silently load `EX-10.1` instead of `EX-10.12`!

#### Enforced Invariants
To permanently guarantee that source selection cannot accidentally match the wrong exhibit:
1. **Exact Suffix Token Matching**: The exhibit identifier must match the exact terminal token:
   `pid.split("_EX_")[-1] == exhibit_id.replace("EX-", "").replace(".", "_")`
2. **Canonical Accession + URL Verification**: Source files are indexed primarily by their immutable SEC document URL (`source_url`) and accession number (`accession_no`), resolving directly to the unique local file path.
3. **Cryptographic SHA-256 Digest**: Every file is verified against its raw SHA-256 hash in [source_identity_corrections.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/design/ui_redesign/phase_04dda/source_identity_corrections.csv).
4. **Automated Test Guard**: Test `test_cik_plus_exhibit_collision_guard` in [tests/test_phase_04dda_audit.py](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/tests/test_phase_04dda_audit.py) mathematically asserts that substring collisions are rejected.
