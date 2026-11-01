# Phase 4D-D Reproduction Instructions
## Deterministic Regeneration and Validation of Dependency Benchmark

### 1. Prerequisites and Environment

- **Python**: Version 3.10+ (standard LexAudit environment)
- **Repository Root**: `f:\projects\nlp\Legal-contract-coherence-auditor-`
- **Required Modules**: Standard library (`csv`, `json`, `hashlib`, `re`, `dataclasses`, `enum`, `typing`) plus project segmentation (`src.segmentation.rule_based`).
- **Dependencies**: No external network access or GPU dependencies required. All operations are local, deterministic, and CPU-efficient.

---

### 2. Step-by-Step Regeneration Workflow

#### Step 1: Candidate Extraction and Dataset Construction

To execute the end-to-end dependency extraction pipeline, resolve antecedents, apply verified perturbations, and export all 8 CSV manifests:

```powershell
python -m src.research.dependency_ground_truth.builder
```

**Expected Console Output**:
```
[Phase 4D-D] Extracting candidates and resolving antecedents...
Extracted 339 dependency candidates and 339 resolution records.
[Phase 4D-D] Building benchmark cases (Positives, Hard Negatives, Ambiguous)...
Constructed 72 benchmark cases:
  - Verified Positives: 30
  - Hard Negatives: 30
  - Ambiguous Cases: 12
[Phase 4D-D] Successfully exported all 8 dataset artifacts.
```

---

#### Step 2: Verification of Generated Artifacts

Verify that all 8 manifests exist and possess valid record counts:

```powershell
python -c "
import csv
for fname in ['dataset_manifest.csv', 'positive_cases.csv', 'negative_cases.csv', 'ambiguous_cases.csv', 'source_family_manifest.csv', 'dependency_candidates.csv', 'antecedent_resolution.csv', 'annotation_queue.csv']:
    with open('research/dependency_ground_truth_phase_04dd/' + fname, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        print(f'{fname}: {len(rows)} records')
"
```

**Expected Verification Counts**:
- `dataset_manifest.csv`: 72 records
- `positive_cases.csv`: 30 records
- `negative_cases.csv`: 30 records
- `ambiguous_cases.csv`: 12 records
- `source_family_manifest.csv`: 10 records
- `dependency_candidates.csv`: 339 records
- `antecedent_resolution.csv`: 339 records
- `annotation_queue.csv`: 72 records

---

#### Step 3: Automated Test Suite Execution

Execute the Phase 4D-D unit and integration test suite to mathematically verify antecedent resolution, boundary checks, and hash immutability:

```powershell
pytest -q tests/test_phase_04dd_dataset.py
```

**Expected Exit Code**: `0` (All tests passing).

---

### 3. Safety and Constraint Enforcement

- **No Neural Inference**: Do **not** execute model benchmarking, fine-tuning, or inference scripts during Phase 4D-D.
- **No Git State Modification**: Do **not** run `git add`, `git commit`, `git push`, or checkout commands.
- **No Threshold Tuning**: Do **not** modify production thresholds or configuration files in `src/config/`.
