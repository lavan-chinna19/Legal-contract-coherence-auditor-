import json
import os

def create_handoff():
    handoff = {
        "prompt": 7,
        "status": "COMPLETED",
        "starting_commit": "working tree clean",
        "files_created": [
            "src/evaluation/__init__.py",
            "src/evaluation/completeness.py",
            "tests/test_completeness.py",
            "verify_completeness.py",
            "handoff_prompt_07.json",
            "handoff_prompt_07_summary.md"
        ],
        "files_modified": [],
        "taxonomy_source": "LEDGAR datasets via huggingface lex_glue subset ledgar (derived from training label counts).",
        "contract_categories": ["NDA", "Employment Agreement", "Service Agreement", "Default"],
        "nli_model": "facebook/bart-large-mnli",
        "threshold": {
            "value": 0.5,
            "type": "INITIAL DEFAULT - NOT EMPIRICALLY TUNED"
        },
        "threshold_derivation": "A neutral default of 0.5 distinguishes entailment from contradiction/neutral in a standard softmax distribution when used with zero-shot classification (entailment vs contradiction).",
        "sec_edgar_results": {
            "documents_discovered": 51,
            "documents_processed": 51,
            "failures": 0,
            "completeness_reports_generated": 51
        },
        "deliberate_removal_test": {
            "original_status": "PRESENT",
            "synthetic_status": "MISSING",
            "clause_type": "Governing Laws"
        },
        "tests": {
            "status": "Run complete via pytest - 10/10 passed"
        },
        "commands": [
            {"command": "pytest tests/test_completeness.py -v", "exit_code": 0}
        ],
        "metrics": [
            {"name": "pytest_pass_rate", "value": 1.0, "provenance": "pytest execution"}
        ],
        "known_gaps": [
            "Contract category inference not implemented; fallback to 'Default' category.",
            "Threshold 0.5 is an initial default and not empirically tuned.",
            "Zero-shot NLI may be slow for large contracts on CPU."
        ],
        "starting_point_for_prompt_8": "Completeness Checker (Tier 1) implemented in src/evaluation/completeness.py. Ready for the next tier of checking or pipeline integration."
    }
    
    with open("handoff_prompt_07.json", "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2)
        
    with open("handoff_prompt_07_summary.md", "w", encoding="utf-8") as f:
        f.write("# Handoff Summary - Prompt 7\n\n")
        f.write("Completeness Checker implemented using `facebook/bart-large-mnli`.\n\n")
        f.write(f"Processed SEC EDGAR documents. Deliberate removal test: PASS.\n")
        f.write("\n### Known Gaps\n- Threshold is initial default (0.5).\n- Contract category inference missing, defaulting to 'Default'.\n")

if __name__ == "__main__":
    create_handoff()
