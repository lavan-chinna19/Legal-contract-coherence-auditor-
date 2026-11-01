# Phase 4D-D Rights, Provenance, and Legal Data Governance Review
## Legal Status, Statutory Framework, and Data Integrity of SEC EDGAR Contracts

### 1. Statutory Framework: 17 U.S.C. § 105 and Third-Party Filings

A widespread misconception in legal NLP research is that any document retrieved from the SEC EDGAR system is automatically in the "public domain" under United States copyright law. Phase 4D-D establishes a rigorous legal analysis of this status:

1. **Scope of 17 U.S.C. § 105**:
   - 17 U.S.C. § 105 provides that copyright protection is not available for any work of the United States Government. This applies to official government publications, statutory texts, agency guidance, and judicial opinions.
   - **Exhibits Filed by Private Registrants**: Material contracts, credit agreements, merger documents, and employment agreements filed under Item 601 of Regulation S-K are authored by private parties, commercial entities, and law firms.
   - The statutory requirement to disclose these agreements publicly to the Securities and Exchange Commission does **not** extinguish private third-party copyright or convert proprietary drafting into public-domain text.
2. **Neither Public Domain nor Categorically Prohibited**:
   - While private contracts are not public domain, neither are they categorically barred from computational linguistics research.
   - Under United States copyright doctrine (17 U.S.C. § 107), non-commercial academic research, linguistic feature extraction, structural analysis, and evaluation benchmarking fall squarely within recognized **fair use** parameters, particularly where:
     - The computational processing is highly transformative (structural dependency auditing).
     - The research does not exploit or substitute for the commercial value of the underlying business transactions.
     - Raw full-text documents are maintained locally for validation rather than redistributing proprietary contract databases for commercial resale.
3. **Formal Classification**:
   - All source material in the Phase 4D-D benchmark is officially classified as:
     `PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED`

---

### 2. Provenance Architecture and Metadata Traceability

Every contract utilized in Phase 4D-D is tracked with full SEC EDGAR metadata in [edgar_manifest.json](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/data/raw/sec_edgar/edgar_manifest.json) and [parent_contract_manifest.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/independent_contract_benchmark_phase_04dc/parent_contract_manifest.csv).

#### Provenance Schema for Utilized Parent Contracts

| Parent Document ID | SEC CIK | Accession Number | Exhibit Type | Form | Cryptographic SHA-256 Hash |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SEC_CIK810136_EX_10_12` | 0000810136 | 0000810136-16-000085 | EX-10.12 | 10-K | `6d6c90539b56f8f5539d91a1e944bc449ea3fb7e7352345517f8b9db77b310d5` |
| `SEC_CIK810136_EX_10_13` | 0000810136 | 0000810136-16-000085 | EX-10.13 | 10-K | `ee141d830b05b3e64fc5f7f3299b9cf9c68705ba324eb798545e855b46e33ca2` |
| `SEC_CIK1090872_EX_10_19` | 0001090872 | 0001090872-16-000070 | EX-10.19 | 10-K | `265a7df4ee23d4677759a2245b780ea3b53c65e8a7d25e0e1eb849202efd3ee6` |
| `SEC_CIK1090872_EX_10_20` | 0001090872 | 0001090872-16-000070 | EX-10.20 | 10-K | `233930b8e957ca169c98ebcf0529ef8956ae5b6f3c155d3ea6ae033ad8ea63ce` |
| `SEC_CIK932021_EX_10_27` | 0000932021 | 0000932021-16-000062 | EX-10.27 | 10-K | `a20dfce93943cf6cb2ca0e657c742337d45f3da117c7ce379b371cb7c0e62058` |
| `SEC_CIK932021_EX_10_28` | 0000932021 | 0000932021-16-000062 | EX-10.28 | 10-K | `e6e0dae95cfc54c30c822ff2e63cbfa35d21c3fa688bf547fe86c2ee7d13e7ae` |
| `SEC_CIK808326_EX_10_9` | 0000808326 | 0000808326-16-000058 | EX-10.9 | 10-K | `07d2f9cb7e7e6008620853bb96bfa8cf0cf748d5d4d3d2aa6dc5877f240fc40c` |
| `SEC_CIK1967306_EX_10_1` | 0001967306 | 0001967306-23-000004 | EX-10.1 | 8-K | `87b5a5b2fc4535310636f3630f9a2fc4aaebaa4764d7df6db874ebf4db11624c` |
| `SEC_CIK1645590_EX_10_35` | 0001645590 | 0001645590-16-000075 | EX-10.35 | 10-K | `b856cbf0ca9c0bc576ceecf9906649727448882fa0f7797491763131718ec2df` |
| `SEC_CIK1101396_EX_10_1` | 0001101396 | 0001101396-16-000045 | EX-10.1 | 10-K | `23ba465f2a1b15c2ec4dfbbcd7e67f70ef8e7ea59419b4931a3194a2152865ff` |

---

### 3. Data Integrity and Transformation Auditing

To maintain scientific integrity across processing stages:
1. **Raw Text Preservation**: Original SEC EDGAR filing text files are stored unmodified in `data/raw/sec_edgar/`.
2. **Cryptographic Hashes**: Every benchmark case in [dataset_manifest.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/dataset_manifest.csv) records both:
   - `source_text_hash`: SHA-256 of the unperturbed full document text.
   - `perturbed_text_hash`: SHA-256 of the reassembled perturbed document text.
3. **Offset Traceability**: Every dependency candidate in [dependency_candidates.csv](file:///f:/projects/nlp/Legal-contract-coherence-auditor-/research/dependency_ground_truth_phase_04dd/dependency_candidates.csv) records exact character start/end offsets (`referencing_char_start`, `referencing_char_end`, `antecedent_char_start`, `antecedent_char_end`) within the clause text.
4. **Non-Destructive Storage**: No raw data or benchmark manifests are overwritten or staged to version control during Phase 4D-D.
