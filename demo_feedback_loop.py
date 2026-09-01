"""
demo_feedback_loop.py — Human-in-the-loop and synthetic feedback generator for Tier 2.
"""
import sys
from src.feedback.reviewer import submit_verdict
from src.feedback.refit import run_refit
from src.feedback.storage import get_all_feedback
from src.config import SEVERITY_HIGH_THRESHOLD, SEVERITY_MED_THRESHOLD

def generate_synthetic_feedback():
    print("Generating SYNTHETIC_TEST feedback...")
    submit_verdict(
        doc_id="synthetic-doc-001",
        clause_id="clause_0_synthetic",
        original_severity="HIGH",
        reviewer_verdict="OVERKILL",
        reviewer_id="synthetic_generator",
        provenance="SYNTHETIC_TEST"
    )
    submit_verdict(
        doc_id="synthetic-doc-001",
        clause_id="clause_1_synthetic",
        original_severity="HIGH",
        reviewer_verdict="OVERKILL",
        reviewer_id="synthetic_generator",
        provenance="SYNTHETIC_TEST"
    )
    submit_verdict(
        doc_id="synthetic-doc-001",
        clause_id="clause_2_synthetic",
        original_severity="HIGH",
        reviewer_verdict="VALID",
        reviewer_id="synthetic_generator",
        provenance="SYNTHETIC_TEST"
    )
    submit_verdict(
        doc_id="synthetic-doc-002",
        clause_id="clause_3_synthetic",
        original_severity="CLEAN",
        reviewer_verdict="MISSED",
        reviewer_id="synthetic_generator",
        provenance="SYNTHETIC_TEST"
    )
    print("Inserted 4 synthetic feedback records.")

def collect_real_feedback():
    print("\n--- HUMAN REVIEWER INTERFACE ---")
    print("Please enter a real verdict for a flagged clause.")
    doc_id = input("Document ID [demo-doc-123]: ").strip() or "demo-doc-123"
    clause_id = input("Clause ID [clause_1]: ").strip() or "clause_1"
    original_severity = input("Original Severity (HIGH/MEDIUM/LOW/CLEAN) [HIGH]: ").strip().upper() or "HIGH"
    
    print("\nVerdicts: VALID, OVERKILL, MISSED, CORRECT")
    verdict = input("Your Verdict: ").strip().upper()
    if verdict not in ["VALID", "OVERKILL", "MISSED", "CORRECT"]:
        print("Invalid verdict. Aborting.")
        return
        
    reviewer_id = input("Reviewer ID (pseudonym) [operator_1]: ").strip() or "operator_1"
    
    record = submit_verdict(
        doc_id=doc_id,
        clause_id=clause_id,
        original_severity=original_severity,
        reviewer_verdict=verdict,
        reviewer_id=reviewer_id,
        provenance="REAL"
    )
    
    print(f"\nSuccessfully stored real human feedback: {record.feedback_id}")

def view_db():
    print("\n--- CURRENT DATABASE RECORDS ---")
    records = get_all_feedback()
    if not records:
        print("No records found.")
    for r in records:
        print(f"[{r.provenance}] {r.original_severity} -> {r.reviewer_verdict} (Doc: {r.doc_id})")
        
def perform_refit():
    print("\n--- RUNNING REFIT JOB ---")
    prov = input("Use 'REAL' or 'SYNTHETIC_TEST' feedback? [SYNTHETIC_TEST]: ").strip().upper() or "SYNTHETIC_TEST"
    old_th, new_th, count = run_refit(provenance=prov)
    
    print(f"\nRefit complete using {count} {prov} records.")
    print(f"Old HIGH: {old_th['SEVERITY_HIGH_THRESHOLD']} -> New HIGH: {new_th['SEVERITY_HIGH_THRESHOLD']}")
    print(f"Old MED:  {old_th['SEVERITY_MED_THRESHOLD']} -> New MED:  {new_th['SEVERITY_MED_THRESHOLD']}")

def main():
    while True:
        print("\n=== PROMPT 11: FEEDBACK LOOP DEMO ===")
        print("1. Generate Synthetic Feedback")
        print("2. Enter Real Human Feedback")
        print("3. View Feedback Database")
        print("4. Run Refit Job")
        print("5. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == '1':
            generate_synthetic_feedback()
        elif choice == '2':
            collect_real_feedback()
        elif choice == '3':
            view_db()
        elif choice == '4':
            perform_refit()
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
