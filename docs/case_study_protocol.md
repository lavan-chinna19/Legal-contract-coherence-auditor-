# Case Study Sourcing Protocol

**Project:** Legal Contract Coherence Auditor  
**Status:** RESEARCH/DEMO PROJECT — not production-ready  
**Last updated:** 2026-08-22

---

## Purpose

This document defines the checklist-driven protocol for finding and verifying
real legal dispute case studies involving structural or clause-ordering defects
in contracts. These case studies serve as qualitative validation anchors — they
are NOT counted toward quantitative metrics.

> **Contract §3 (Case-Study Integrity):** Every "verified real case study" must
> be genuinely sourced, checked for public availability of full text, and cited
> with its actual source. The count of verified studies must be stated honestly,
> even if that number is zero.

---

## Verification Checklist (per candidate case study)

For each candidate, all boxes must be checked before marking it "verified":

- [ ] **Source identified** — name of court, tribunal, or published report
- [ ] **Public availability confirmed** — full text (or official summary) is
      freely accessible without paywall (e.g., court docket, PACER, official
      government site, Casetext public domain)
- [ ] **Structural/clause defect confirmed** — the dispute explicitly involves
      clause ordering, missing clauses, contradictory provisions, or reference
      errors (not merely a payment or performance dispute)
- [ ] **URL or citation recorded** — exact URL or legal citation (case name,
      court, year, docket number) noted below
- [ ] **Full text or official summary retrieved and readable** — not paraphrased
      from a secondary source
- [ ] **Date of retrieval recorded**

---

## Candidate Log

### Candidate 1 — Raffles v. Wichelhaus (1864)

| Field | Value |
|---|---|
| Citation | Raffles v. Wichelhaus (1864) 2 H&C 906 |
| Court | Court of Exchequer, England |
| Structural defect type | Ambiguous reference — two ships named "Peerless"; contract referenced both without disambiguation |
| Public availability | Available in historical law reports; free summaries on multiple law school sites |
| Full text public? | Official report in historical archives; freely summarized but original report may require library access |
| Structural/clause defect confirmed? | YES — a reference ambiguity (which "Peerless") voided the contract; directly analogous to reference-resolution checker |
| URL | https://en.wikipedia.org/wiki/Raffles_v_Wichelhaus (summary); full text: 2 H&C 906 (1864) |
| Retrieved | 2026-08-22 |
| **Verification status** | **PARTIALLY VERIFIED** — structural defect confirmed, public summary available, but full original court report text requires library/Westlaw access. Cited as historical authority only. |

---

### Candidate 2 — ProCD, Inc. v. Zeidenberg (7th Cir. 1996)

| Field | Value |
|---|---|
| Citation | ProCD, Inc. v. Zeidenberg, 86 F.3d 1447 (7th Cir. 1996) |
| Court | United States Court of Appeals, Seventh Circuit |
| Structural defect type | Clause ordering / formation — license terms appeared inside the box after purchase; question of whether terms presented after transaction are binding |
| Public availability | Full text freely available on Google Scholar, CourtListener (PACER) |
| Full text public? | YES — https://law.justia.com/cases/federal/appellate-courts/F3/86/1447/598812/ |
| Structural/clause defect confirmed? | YES — dispute centres on the sequence and timing of when license terms were presented relative to contract formation |
| URL | https://law.justia.com/cases/federal/appellate-courts/F3/86/1447/598812/ |
| Retrieved | 2026-08-22 |
| **Verification status** | **VERIFIED** — full text publicly available; structural clause-order issue confirmed from case text. |

---

### Candidate 3 — (No additional verified candidate found)

| Field | Value |
|---|---|
| Search performed | Searched Casetext, CourtListener, Google Scholar for "contract clause order dispute" "missing clause" "contract structure defect" |
| Result | No additional case found with (a) full public text AND (b) explicit structural/clause-ordering defect as primary issue, within time available for this prompt |
| **Verification status** | **NOT FOUND** |

---

## Honest Count

| Status | Count |
|---|---|
| Fully verified (full public text, structural defect confirmed) | **1** (ProCD v. Zeidenberg) |
| Partially verified (structural defect confirmed, full text requires library access) | **1** (Raffles v. Wichelhaus) |
| Not found / not verified | **0 additional** |
| Fabricated or unverified cases presented as verified | **0** |

**Total verified by Contract §3 standard: 1 fully, 1 partially.**  
The project description targeted 2–3. One is fully verified with public full text.
The historical Raffles case is well-established doctrine but original text is not
freely online in full; it is recorded as partial.

---

## Protocol for Future Prompts

If additional case studies are needed:
1. Search CourtListener (https://www.courtlistener.com/) — free full-text US case law
2. Search Google Scholar (https://scholar.google.com/) — Case law tab
3. Search Casetext (https://casetext.com/) — free tier available
4. Candidate must pass ALL checklist items above before being marked verified
5. Do NOT paraphrase or reconstruct a case from secondary sources — primary text or
   official summary only
