# LexAudit Research — Benchmark Reproduction Instructions
<!-- Reference copy for research archive -->

## 1. Prerequisites
- Python 3.11 with PyTorch 2.6 (CPU or CUDA).
- Dependencies: `pip install -r requirements.txt`.
- Checkpoints present: `models/coherence_classifier.pt` and cache for `nlpaueb/legal-bert-base-uncased`.

## 2. Command-Line Reproduction

### Step 1: Scientific Parity & Runtime Scaling
```powershell
pytest tests/test_repositioning.py -v
python scripts/benchmark_repositioning_parity_and_runtime.py
```
Outputs:
- `design/ui_redesign/phase_04c/optimized_rescoring_parity.csv`
- `design/ui_redesign/phase_04c/runtime_benchmark.csv`

### Step 2: Synthetic Displacement Recovery Benchmark
```powershell
python scripts/run_synthetic_recovery_benchmark.py
```
Outputs:
- `design/ui_redesign/phase_04c/position_recovery_results.json`
- `design/ui_redesign/phase_04c/baseline_comparison.csv`

### Step 3: Backend Regression Suite
```powershell
pytest tests/ -v
```
Expected: 131 passed, 2 skipped in ~95 seconds.

### Step 4: Frontend Validation & Build
```powershell
cd frontend
node node_modules/typescript/bin/tsc --noEmit
node node_modules/eslint/bin/eslint.js src/
npm run test:alignment
npm run build
```

### Step 5: Headless Browser CDP Verification
```powershell
python scripts/run_phase4c_browser_verification.py
```
Expected: 14/14 tests PASSED, 8 evidence screenshots generated.
