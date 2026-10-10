import json

def create_handoff():
    handoff = {
        "prompt": 8,
        "status": "COMPLETED",
        "starting_commit": "be4670c",
        "files_created": [
            "src/scoring/ensemble.py",
            "tests/test_ensemble.py",
            "evaluate_ensemble.py",
            "handoff_prompt_08.json",
            "handoff_prompt_08_summary.md"
        ],
        "files_modified": [],
        "evaluation_dataset": "SEC EDGAR Form 10-K Exhibit 10 & LEDGAR clause types",
        "sample_size": 3,
        "fine_tuned_only": {
            "mode": "fine_tuned",
            "alpha": 1.0,
            "delta_anomaly": 0.0050
        },
        "zero_shot_only": {
            "mode": "zero_shot",
            "alpha": 0.0,
            "delta_anomaly": 0.0
        },
        "combined": {
            "mode": "combined",
            "alpha": 0.5,
            "delta_anomaly": 0.0025
        },
        "ensemble_formula": "combined_score = alpha * fine_tuned_score + (1 - alpha) * zero_shot_score",
        "ensemble_weight": {
            "alpha": 0.5,
            "derivation": "INITIAL DEFAULT - NOT EMPIRICALLY TUNED"
        },
        "weight_tuning": {
            "0.25": 0.0013,
            "0.50": 0.0025,
            "0.75": 0.0038
        },
        "tests": {
            "pytest_result": "3 passed, 1 warning in 62.56s",
            "coverage": "Unit tests cover fine-tuned-only, zero-shot-only, combined modes, weighted score calculations, and zero-shot baseline."
        },
        "commands": [
            {"command": "python evaluate_ensemble.py", "exit_code": 0},
            {"command": "pytest tests/test_ensemble.py", "exit_code": 0}
        ],
        "metrics": [
            {"name": "fine_tuned_delta", "value": 0.0050, "provenance": "evaluate_ensemble.py output"},
            {"name": "zero_shot_delta", "value": 0.0, "provenance": "evaluate_ensemble.py output"},
            {"name": "combined_delta", "value": 0.0025, "provenance": "evaluate_ensemble.py output"}
        ],
        "known_gaps": [
            "Zero-shot completeness score is order-invariant, providing no sensitivity to shuffled transitions.",
            "Combined ensemble did not improve over the stronger baseline (fine-tuned).",
            "Alpha weight is unoptimized and defaults to 0.5."
        ],
        "starting_point_for_prompt_9": "Ensemble architecture for Channel B is established. We have separate access to fine-tuned, zero-shot, and combined scores. Ready for downstream integration."
    }

    with open("handoff_prompt_08.json", "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2)

    with open("handoff_prompt_08_summary.md", "w", encoding="utf-8") as f:
        f.write("# Handoff Summary - Prompt 8\n\n")
        f.write("Implemented score ensembling for Channel-B signals combining Fine-Tuned transition scores and Zero-Shot completeness scores.\n\n")
        f.write("### Evaluation Results\n")
        f.write("- **Fine-tuned only delta:** +0.0050\n")
        f.write("- **Zero-shot only delta:** +0.0000\n")
        f.write("- **Combined delta (a=0.5):** +0.0025\n\n")
        f.write("### Conclusion\n")
        f.write("**Combined ensemble did not improve over the stronger baseline.** The zero-shot completeness checker is order-invariant and lacks sensitivity to shuffled anomalies.\n\n")
        f.write("### Next Steps\n")
        f.write("Prompt 9 can leverage these structured metrics for downstream tasks or visualizations.\n")

if __name__ == "__main__":
    create_handoff()
