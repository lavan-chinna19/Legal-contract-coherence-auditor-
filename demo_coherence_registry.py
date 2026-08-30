"""
demo_coherence_registry.py — Verification script demonstrating:
1. End-to-end Zero-Shot Coherence path (Gate 3).
2. Swapping Fine-Tuned and Zero-Shot models via the unified registry (Gate 4).
"""
import time
from src.config import ClauseRecord
from src.coherence.factory import get_coherence_model


def run_demo():
    print("=" * 65)
    print("DEMONSTRATION: Swappable Discourse Coherence Model Registry")
    print("=" * 65)

    # 1. Construct Sample Real-world Clause Pairs
    coherent_clause_a = ClauseRecord(
        clause_id="demo_0",
        doc_id="contract_alpha",
        text="Section 4.01. Payment Terms. The Purchaser shall pay all invoiced amounts within thirty (30) days of receipt of invoice.",
        label="Payment",
        sequence_idx=0,
        char_start=0,
        char_end=120,
        source="demo"
    )

    coherent_clause_b = ClauseRecord(
        clause_id="demo_1",
        doc_id="contract_alpha",
        text="Section 4.02. Late Payments. Any overdue payments shall accrue interest at a rate of 1.5% per month or the maximum rate permitted by law.",
        label="Payment",
        sequence_idx=1,
        char_start=121,
        char_end=260,
        source="demo"
    )

    incoherent_clause_c = ClauseRecord(
        clause_id="demo_c",
        doc_id="contract_beta",
        text="Section 12.08. Environmental Indemnity. The Tenant agrees to remediate all hazardous chemical discharges occurring on the leased premises.",
        label="Environmental",
        sequence_idx=45,
        char_start=0,
        char_end=150,
        source="demo"
    )

    print("\n--- Test Pairs Defined ---")
    print("Pair 1 (Coherent - Consecutive Payment Terms):")
    print(f"  [A]: {coherent_clause_a.text}")
    print(f"  [B]: {coherent_clause_b.text}")
    print("\nPair 2 (Incoherent - Payment to Environmental Discontinuity):")
    print(f"  [A]: {coherent_clause_a.text}")
    print(f"  [C]: {incoherent_clause_c.text}")

    # 2. Test Fine-Tuned Model Path
    print("\n" + "-" * 50)
    print("1. Testing Fine-Tuned Coherence Model Path")
    print("-" * 50)
    fine_tuned_model = get_coherence_model("fine_tuned")
    print(f"Loaded: {fine_tuned_model.name}")
    
    score_coherent_ft = fine_tuned_model.score_pair(coherent_clause_a, coherent_clause_b)
    score_incoherent_ft = fine_tuned_model.score_pair(coherent_clause_a, incoherent_clause_c)
    
    print(f"  Coherent Pair Score:   {score_coherent_ft:.4f}")
    print(f"  Incoherent Pair Score: {score_incoherent_ft:.4f}")
    assert 0.0 <= score_coherent_ft <= 1.0
    assert 0.0 <= score_incoherent_ft <= 1.0

    # 3. Test Zero-Shot Open-Source LLM Path (Gate 3)
    print("\n" + "-" * 50)
    print("2. Testing Zero-Shot Alternative Path (Gate 3)")
    print("-" * 50)
    zero_shot_model = get_coherence_model("zero_shot")
    print(f"Loaded: {zero_shot_model.name}")
    
    score_coherent_zs = zero_shot_model.score_pair(coherent_clause_a, coherent_clause_b)
    score_incoherent_zs = zero_shot_model.score_pair(coherent_clause_a, incoherent_clause_c)
    
    print(f"  Coherent Pair Score:   {score_coherent_zs:.4f}")
    print(f"  Incoherent Pair Score: {score_incoherent_zs:.4f}")
    assert 0.0 <= score_coherent_zs <= 1.0
    assert 0.0 <= score_incoherent_zs <= 1.0

    # 4. Summary Table
    print("\n" + "=" * 65)
    print(f"{'Model Path':<25} | {'Coherent Transition':<20} | {'Incoherent Jump':<15}")
    print("-" * 65)
    print(f"{'fine_tuned':<25} | {score_coherent_ft:<20.4f} | {score_incoherent_ft:<15.4f}")
    print(f"{'zero_shot':<25} | {score_coherent_zs:<20.4f} | {score_incoherent_zs:<15.4f}")
    print("=" * 65)
    print("STATUS: PASS (Acceptance Gates 3 & 4 Verified)")


if __name__ == "__main__":
    run_demo()
