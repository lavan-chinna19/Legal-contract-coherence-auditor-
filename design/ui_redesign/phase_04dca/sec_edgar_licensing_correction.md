# SEC EDGAR Copyright, Licensing & Source Rights Audit

**Audit Program**: LexAudit Legal NLP & Data Integrity Audit (Phase 4D-C-A)  
**Investigation Scope**: Audit D — Correction of 17 U.S.C. §105 Public Domain Claims  
**Auditor**: Legal NLP Evaluation Specialist, Research Rights Compliance Specialist  
**Authoritative Classification**: **`PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED`**

---

## 1. Legal Error Identification & Statutory Correction

### The Erroneous Historical Claim
The Phase 4D-C provenance manifest (`src/research/independent_benchmark/provenance.py`, line 134) and associated documentation stated:
```text
license_status = "PUBLIC_DOMAIN_US_FEDERAL_FILING"
```
The narrative report asserted that because agreements were retrieved from the SEC EDGAR system, they are automatically public domain works under 17 U.S.C. §105.

### The Authoritative Statutory Correction
Under Title 17 of the United States Code (17 U.S.C. §105):
> "Copyright protection under this title is not available for any work of the United States Government..."

Section 101 defines a "work of the United States Government" as:
> "...a work prepared by an officer or employee of the United States Government as part of that person's official duties."

**Material commercial contracts (Exhibit 10) filed on EDGAR are authored by private commercial corporations, in-house counsel, and private law firms**. Filing an agreement with the Securities and Exchange Commission to satisfy federal disclosure obligations under the Securities Act of 1933 or the Securities Exchange Act of 1934 **does not convert a privately authored work into a work of the United States Government, nor does it extinguish private copyright or inject the text into the public domain**.

---

## 2. Essential Legal Distinctions for Research NLP

To maintain legal precision and compliance, the research team must observe the following distinctions:

```
+-----------------------------------------------------------------------------------------+
|                               SEC EDGAR CONTRACT STATUS                                 |
+-----------------------------------------------------------------------------------------+
| 1. Public Accessibility                                                                 |
|    Mandated by federal securities disclosure laws; freely viewable on sec.gov.          |
+-----------------------------------------------------------------------------------------+
| 2. Authorship & Ownership                                                               |
|    Privately drafted by commercial contracting entities; NOT U.S. Government works.     |
+-----------------------------------------------------------------------------------------+
| 3. Internal Non-Commercial Research Use                                                 |
|    Permitted under Fair Use doctrine (17 U.S.C. §107) for computational linguistics,    |
|    feature extraction, model evaluation, and benchmark scoring.                         |
+-----------------------------------------------------------------------------------------+
| 4. Corpus Redistribution                                                                |
|    Redistributing complete verbatim contract text carries copyright uncertainty.        |
|    Classified as: PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED.                              |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Privacy, Personal Information & SEC Access Policies

1. **PII and Redaction**: Official SEC filings may contain executive signatures, addresses, and compensation schedules. While public disclosures under SEC rules, commercial distribution requires screening for sensitive personal data.
2. **SEC Fair Access Policy**: Retrieval of EDGAR data must comply with the SEC Fair Access Policy (maximum 10 requests per second with declared `User-Agent` headers).
3. **No Commercial Re-Licensing**: The benchmark project cannot license the raw contract text under MIT, Apache, or CC-BY, as the project does not own the underlying literary copyrights.

---

## 4. Benchmark Distribution Policy & Recommendations

To maintain reproducibility while strictly mitigating copyright and redistribution risks:
1. **Zero Raw Text Redistribution**: Benchmark outputs published to public repositories shall **not** include the full raw text of the 32 parent contracts.
2. **Standalone Provenance Packaging**: Distribute benchmark reproduction packages containing:
   - SEC Accession Number (e.g., `0001493152-23-046428`)
   - Direct SEC EDGAR URL link (e.g., `https://www.sec.gov/Archives/edgar/data/...`)
   - Cryptographic SHA-256 digests of raw and normalized text
   - Automated fetch and extraction scripts
   - Character offsets and sequence IDs
   - Deterministic transformation recipes and perturbation seeds
3. **Formal Status Classification**: All dataset records and handoff manifests are hereby updated to:
   $$\mathbf{PUBLICLY\_ACCESSIBLE\_RIGHTS\_UNDETERMINED}$$
