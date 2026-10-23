"""
src/redteam/scenarios.py — Pre-declared canonical scenario catalog for reproducible red-team evaluation.
Covers P1 through P10 across Straightforward, Moderate, and Difficult tiers.
"""
from typing import List
from src.redteam.schema import (
    PerturbationType,
    PerturbationDifficulty,
    PerturbationScenario
)


def get_canonical_benchmark_scenarios() -> List[PerturbationScenario]:
    """
    Returns 20 independently constructed, typed benchmark scenarios across 10 categories.
    """
    scenarios = [
        # P1: Displacement
        PerturbationScenario(
            scenario_id="SCEN_P1_01_DISP_DISTANT",
            perturbation_type=PerturbationType.P1_DISPLACEMENT,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Distant Clause Displacement",
            description="Move Section 2 (Scope of Services) from Slot 1 to Slot 9 (end of contract).",
            target_clause_ids=["SYNTH_DOC_01_MSA_c01"],
            parameters={"source_slot": 1, "target_slot": 10},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL",
            seed=42,
            limitations="Channel A is position-invariant; detection depends entirely on discourse transition sensitivity."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P1_02_DISP_MODERATE",
            perturbation_type=PerturbationType.P1_DISPLACEMENT,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Moderate Clause Displacement",
            description="Move Section 6 (Term and Termination) from Slot 5 to Slot 2.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c05"],
            parameters={"source_slot": 5, "target_slot": 2},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL",
            seed=42,
            limitations="Displacement across 3 slots perturbs multiple local transition boundaries."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P1_03_DISP_SUBTLE",
            perturbation_type=PerturbationType.P1_DISPLACEMENT,
            difficulty=PerturbationDifficulty.LEVEL_3_DIFFICULT,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Subtle Local Displacement",
            description="Move Section 4 (Intellectual Property) from Slot 3 to Slot 4 (single-slot shift).",
            target_clause_ids=["SYNTH_DOC_01_MSA_c03"],
            parameters={"source_slot": 3, "target_slot": 4},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL",
            seed=42,
            limitations="Single-slot displacement produces smaller discourse score shifts than distant moves."
        ),

        # P2: Clause Swapping
        PerturbationScenario(
            scenario_id="SCEN_P2_01_SWAP_ADJACENT",
            perturbation_type=PerturbationType.P2_SWAP,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Adjacent Clause Swap",
            description="Swap Section 1 (Preamble) and Section 2 (Scope of Services).",
            target_clause_ids=["SYNTH_DOC_01_MSA_c00", "SYNTH_DOC_01_MSA_c01"],
            parameters={"slot_a": 0, "slot_b": 1},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL",
            seed=42,
            limitations="Preamble displacement directly violates standard opening legal convention."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P2_02_SWAP_DISTANT",
            perturbation_type=PerturbationType.P2_SWAP,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Distant Clause Swap",
            description="Swap Section 3 (Payment Terms) and Section 9 (Governing Law).",
            target_clause_ids=["SYNTH_DOC_01_MSA_c02", "SYNTH_DOC_01_MSA_c08"],
            parameters={"slot_a": 2, "slot_b": 8},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL",
            seed=42,
            limitations="Perturbs up to four discourse transition edges simultaneously."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P2_03_SWAP_SUBTLE",
            perturbation_type=PerturbationType.P2_SWAP,
            difficulty=PerturbationDifficulty.LEVEL_3_DIFFICULT,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Subtle Semantic Swap",
            description="Swap Section 5 (Confidentiality) and Section 7 (Indemnification).",
            target_clause_ids=["SYNTH_DOC_01_MSA_c04", "SYNTH_DOC_01_MSA_c06"],
            parameters={"slot_a": 4, "slot_b": 6},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL",
            seed=42,
            limitations="Both clauses represent standard risk-allocation boilerplate; discourse shifts may be modest."
        ),

        # P3: Exact Duplication
        PerturbationScenario(
            scenario_id="SCEN_P3_01_DUP_EXACT",
            perturbation_type=PerturbationType.P3_EXACT_DUPLICATION,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Exact Clause Duplication (Confidentiality)",
            description="Duplicate Section 5 (Confidentiality) and insert an identical copy at Slot 8.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c04"],
            parameters={"source_slot": 4, "insert_slot": 8},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL (DESCRIPTIVE)",
            seed=42,
            limitations="DEDICATED_DUPLICATE_DETECTOR_UNAVAILABLE: System lacks dedicated duplication rule checker."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P3_02_DUP_EXACT_SLA",
            perturbation_type=PerturbationType.P3_EXACT_DUPLICATION,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_02_SLA",
            title="Exact Clause Duplication (Warranty)",
            description="Duplicate Section 5 (Warranty Disclaimer) and insert at Slot 2 in SLA.",
            target_clause_ids=["SYNTH_DOC_02_SLA_c04"],
            parameters={"source_slot": 4, "insert_slot": 2},
            expected_detector="CHANNEL_B_DISCOURSE_MODEL (DESCRIPTIVE)",
            seed=42,
            limitations="Evaluated descriptively; duplicate detection is not a formal model capability."
        ),

        # P4: Near-Duplicate
        PerturbationScenario(
            scenario_id="SCEN_P4_01_NEAR_DUP",
            perturbation_type=PerturbationType.P4_NEAR_DUPLICATION,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Lexical Variant Near-Duplicate",
            description="Insert a near-duplicate variant of Section 5 using legal synonym substitution at Slot 8.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c04"],
            parameters={"source_slot": 4, "insert_slot": 8, "substitution_mode": "SYNONYM_REPLACEMENT"},
            expected_detector="CHANNEL_A_OOD_MODEL (EXPLORATORY)",
            seed=42,
            limitations="Exploratory test: semantic near-duplicates do not necessarily trigger OOD distance spikes."
        ),

        # P5: Broken Internal Cross-Reference
        PerturbationScenario(
            scenario_id="SCEN_P5_01_BROKEN_REF_SEC99",
            perturbation_type=PerturbationType.P5_BROKEN_REFERENCE,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Dangling Internal Reference (Section 99)",
            description="Mutate citation in Section 4 from 'Section 2' to nonexistent 'Section 99'.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c03"],
            parameters={"old_target_sec": "2", "new_nonexistent_sec": "Section 99"},
            expected_detector="CROSS_REFERENCE_CHECKER",
            seed=42,
            limitations="Evaluates CrossReferenceChecker dangling section citation resolution."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P5_02_BROKEN_REF_SEC88",
            perturbation_type=PerturbationType.P5_BROKEN_REFERENCE,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Dangling Internal Reference in Indemnification",
            description="Mutate citation in Section 7 from 'Section 5' to nonexistent 'Section 88'.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c06"],
            parameters={"old_target_sec": "5", "new_nonexistent_sec": "Section 88"},
            expected_detector="CROSS_REFERENCE_CHECKER",
            seed=42,
            limitations="Requires spaCy pattern matcher to identify Section 88 as undeclared target."
        ),

        # P6: Missing Exhibit Reference
        PerturbationScenario(
            scenario_id="SCEN_P6_01_MISSING_EXHIBIT_Z",
            perturbation_type=PerturbationType.P6_MISSING_EXHIBIT,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Undeclared Exhibit Citation (Exhibit Z)",
            description="Mutate Exhibit A citation in Section 2 to undeclared 'Exhibit Z'.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c01"],
            parameters={"new_nonexistent_exhibit": "Exhibit Z"},
            expected_detector="CROSS_REFERENCE_CHECKER",
            seed=42,
            limitations="Evaluates whether CrossReferenceChecker extracts Exhibit citations against inventory."
        ),

        # P7: Date Chronology Inversion
        PerturbationScenario(
            scenario_id="SCEN_P7_01_INVERTED_TERM",
            perturbation_type=PerturbationType.P7_DATE_INVERSION,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Inverted Contract Term (Termination before Effective)",
            description="Mutate Section 6 termination date to 'December 31, 2020' (prior to Jan 1, 2025 effective date).",
            target_clause_ids=["SYNTH_DOC_01_MSA_c05"],
            parameters={"inversion_type": "INVERTED_CONTRACT_TERM", "new_date_str": "December 31, 2020"},
            expected_detector="DATE_LOGIC_CHECKER",
            seed=42,
            limitations="Evaluates DateLogicChecker chronology rule for explicit term inversion."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P7_02_INVERTED_PAYMENT",
            perturbation_type=PerturbationType.P7_DATE_INVERSION,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Inverted Payment Due Date",
            description="Set payment due date in Section 3 to precede the contract effective date.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c02"],
            parameters={"inversion_type": "INVALID_PAYMENT_TIMELINE", "new_date_str": "December 15, 2024"},
            expected_detector="DATE_LOGIC_CHECKER",
            seed=42,
            limitations="Tests relationship between Effective Date and Payment Due Date."
        ),

        # P8: Clause Deletion
        PerturbationScenario(
            scenario_id="SCEN_P8_01_DELETION_WITH_CONSEQUENCE",
            perturbation_type=PerturbationType.P8_DELETION,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Clause Deletion Creating Dangling Reference",
            description="Delete Section 2 (Scope of Services), which Section 4 explicitly cites.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c01"],
            parameters={"target_slot": 1},
            expected_detector="CROSS_REFERENCE_CHECKER",
            seed=42,
            limitations="Deletion is only strictly evaluated when it produces an independently verifiable dangling reference."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P8_02_DELETION_DESCRIPTIVE",
            perturbation_type=PerturbationType.P8_DELETION,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Arbitrary Boilerplate Deletion",
            description="Delete Section 8 (Limitation of Liability) without surviving reference dependencies.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c07"],
            parameters={"target_slot": 7},
            expected_detector="NONE (DESCRIPTIVE_ONLY)",
            seed=42,
            limitations="DESCRIPTIVE_ONLY: System has no completeness oracle; deletion of optional clause is not automatically an error."
        ),

        # P9: Clean Negative Control
        PerturbationScenario(
            scenario_id="SCEN_P9_01_CLEAN_CONTROL_MSA",
            perturbation_type=PerturbationType.P9_NEGATIVE_CONTROL,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Clean Negative Control (MSA)",
            description="Untouched 10-clause Master Services Agreement baseline with zero synthetic alterations.",
            target_clause_ids=[],
            parameters={},
            expected_detector="NONE (EXPECT_NO_ANOMALY)",
            seed=42,
            limitations="Must produce zero spurious rule violations."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P9_02_CLEAN_CONTROL_SLA",
            perturbation_type=PerturbationType.P9_NEGATIVE_CONTROL,
            difficulty=PerturbationDifficulty.LEVEL_1_STRAIGHTFORWARD,
            source_doc_id="SYNTH_DOC_02_SLA",
            title="Clean Negative Control (SLA)",
            description="Untouched 8-clause Software License Agreement baseline.",
            target_clause_ids=[],
            parameters={},
            expected_detector="NONE (EXPECT_NO_ANOMALY)",
            seed=42,
            limitations="Must verify negative-control false-positive bounds."
        ),

        # P10: Combined Perturbations
        PerturbationScenario(
            scenario_id="SCEN_P10_01_COMBINED_DISP_AND_REF",
            perturbation_type=PerturbationType.P10_COMBINED,
            difficulty=PerturbationDifficulty.LEVEL_2_MODERATE,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Compound: Displacement + Broken Reference",
            description="Displace Section 2 to end of contract AND mutate Section 7 to cite nonexistent Section 99.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c01", "SYNTH_DOC_01_MSA_c06"],
            parameters={
                "steps": [
                    {"type": "P1_DISPLACEMENT", "source_slot": 1, "target_slot": 9},
                    {"type": "P5_BROKEN_REFERENCE", "target_clause_id": "SYNTH_DOC_01_MSA_c06", "old_target_sec": "5", "new_sec": "Section 99"}
                ]
            },
            expected_detector="MULTI_DETECTOR_ENSEMBLE",
            seed=42,
            limitations="Tests whether simultaneous structural and rule defects interact non-additively."
        ),
        PerturbationScenario(
            scenario_id="SCEN_P10_02_COMBINED_DATE_AND_DUP",
            perturbation_type=PerturbationType.P10_COMBINED,
            difficulty=PerturbationDifficulty.LEVEL_3_DIFFICULT,
            source_doc_id="SYNTH_DOC_01_MSA",
            title="Compound: Date Inversion + Duplication",
            description="Invert termination date to 2020 AND duplicate Section 5 (Confidentiality) at Slot 8.",
            target_clause_ids=["SYNTH_DOC_01_MSA_c05", "SYNTH_DOC_01_MSA_c04"],
            parameters={
                "steps": [
                    {"type": "P7_DATE_INVERSION", "target_clause_id": "SYNTH_DOC_01_MSA_c05", "date_str": "December 31, 2020"},
                    {"type": "P3_EXACT_DUPLICATION", "source_slot": 4, "insert_slot": 8}
                ]
            },
            expected_detector="MULTI_DETECTOR_ENSEMBLE",
            seed=42,
            limitations="Assesses combined date-rule violation alongside discourse transition anomaly."
        )
    ]
    return scenarios
