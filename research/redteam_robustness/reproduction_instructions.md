# Phase 4D Benchmark Reproduction Instructions

To reproduce all 20 canonical scenario evaluations and regenerate the 21 research artifacts:

```bash
python -c "from src.redteam.reporting import run_full_benchmark_and_generate_artifacts; run_full_benchmark_and_generate_artifacts()"
```

To run the unit test suite:
```bash
pytest tests/test_redteam_transformations.py tests/test_redteam_oracle.py tests/test_redteam_runner.py -v
```
