# Evidence Index (Prompt 23)

**Phase:** Prompt 23 — Evidence Registry  
**Directory:** `audit/prompt_23/evidence/`  
**Date:** 2026-10-10  

---

## Evidence Artifacts Mapping

| Artifact Name | Path | Description / Contents | Associated Acceptance Test IDs | Verification Method |
| :--- | :--- | :--- | :--- | :--- |
| `initial_page_load.png` | `audit/prompt_23/evidence/initial_page_load.png` | High-resolution browser screenshot of initial UI render at `http://localhost:3000` | UI-01 to UI-12, ENV-01 | Real browser viewport capture |
| `ui_initial_inventory.webp` | `brain/.../ui_initial_inventory_1791619347089.webp` | Screen recording of browser session verifying element layout and online status | Gate 2, ENV-01 | Automated browser interaction video |
| `acceptance_test_results.json` | `audit/prompt_23/evidence/acceptance_test_results.json` | Full structured JSON telemetry of 32 live acceptance tests | ENV-01 to NEG-04 (all 32 tests) | Automated HTTP test harness |
| `performance_telemetry.json` | `audit/prompt_23/evidence/performance_telemetry.json` | Measured wall-clock durations for upload, pipeline inference, and XAI | ANL-01, ANL-02, XAI-01, XAI-02, Gate 14 | High-resolution timing metrics |
| `sample_analysis_result_multiclause.json` | `audit/prompt_23/evidence/sample_analysis_result_multiclause.json` | Raw API response for 5-clause agreement analysis | ANL-02, SEG-01, SEG-02, COH-01, COH-02 | Live HTTP API JSON output |
| `sample_abrupt_shift_result.json` | `audit/prompt_23/evidence/sample_abrupt_shift_result.json` | Raw API response for semantic topic shift probe (quantum mechanics clause) | COH-03 | Live HTTP API JSON output |
| `sample_rule_violations_result.json` | `audit/prompt_23/evidence/sample_rule_violations_result.json` | Raw API response verifying broken Section 99 reference and inverted dates | RUL-01 | Live HTTP API JSON output |
| `sample_xai_attribution.json` | `audit/prompt_23/evidence/sample_xai_attribution.json` | Raw JSON response for Channel A Integrated Gradients token attributions | XAI-01 | Live HTTP API JSON output |
| `sample_xai_sensitivity.json` | `audit/prompt_23/evidence/sample_xai_sensitivity.json` | Raw JSON response for Channel B neighborhood perturbation sensitivity | XAI-02 | Live HTTP API JSON output |
| `fixtures/valid_small.txt` | `audit/prompt_23/evidence/fixtures/valid_small.txt` | Isolated 2-clause legal contract fixture | UPL-01, ANL-01 | Source text fixture |
| `fixtures/valid_multiclause.txt`| `audit/prompt_23/evidence/fixtures/valid_multiclause.txt`| Isolated 5-clause representative NDA contract fixture | UPL-02, ANL-02, SEG-01 | Source text fixture |
| `fixtures/rule_violations.txt` | `audit/prompt_23/evidence/fixtures/rule_violations.txt` | Synthetic contract probe containing broken cross-references and inverted dates | RUL-01 | Source text fixture |
| `fixtures/abrupt_shift.txt` | `audit/prompt_23/evidence/fixtures/abrupt_shift.txt` | Synthetic contract probe with out-of-domain quantum mechanics clause | COH-03 | Source text fixture |
| `fixtures/empty.txt` | `audit/prompt_23/evidence/fixtures/empty.txt` | Zero-byte empty file fixture for negative upload testing | UPL-03 | Negative test fixture |
| `fixtures/invalid_binary.bin` | `audit/prompt_23/evidence/fixtures/invalid_binary.bin` | Non-UTF8 binary byte sequence for encoding rejection verification | UPL-04 | Negative test fixture |
