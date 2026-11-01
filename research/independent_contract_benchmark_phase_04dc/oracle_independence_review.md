# Oracle and Candidate Independence Review

## Defect Addressed from Phase 4D-B Audit
In the Phase 4D-B evaluation, Candidate C3 achieved 2/2 recall on held-out synthetic cases because test perturbations were constructed using the same heading-lifecycle conditions that C3's rule DAG checks.

## Phase 4D-C Independent Oracle Implementation
1. **Independence from Model Predictions**: The Phase 4D-C Oracle (`IndependentGroundTruthOracle`) does NOT import, inspect, or depend on Candidate C3's DAG rules, heading classifications, or model scores.
2. **Objective Discourse Ground Truth**: Positive cases are verified through deterministic inspection of backward discourse markers (`"the preceding provision"`, `"subject to the immediately preceding"`, `"as defined above"`). A positive label (`VERIFIED_DISCOURSE_DEPENDENCY_VIOLATION`) is assigned ONLY when an anaphoric presupposition is broken by clause repositioning.
3. **Exclusion of Ambiguous Cases**: Non-canonical ordering permutations lacking verifiable textual dependencies are strictly marked `AMBIGUOUS` and excluded from binary detection metrics.
