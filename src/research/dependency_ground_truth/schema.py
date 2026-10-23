"""
src/research/dependency_ground_truth/schema.py
Data schemas and enums for Phase 4D-D Contract Dependency Ground Truth.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class DependencyClass(str, Enum):
    CROSS_CLAUSE_SECTION = "CROSS_CLAUSE_SECTION_REFERENCE"
    INTRA_CLAUSE_DISCOURSE = "INTRA_CLAUSE_DISCOURSE_MARKER"
    CROSS_CLAUSE_DISCOURSE = "CROSS_CLAUSE_DISCOURSE_REFERENCE"
    HIERARCHICAL_SUBSECTION = "HIERARCHICAL_SUBSECTION_REFERENCE"
    DEFINED_TERM_CROSS_CLAUSE = "DEFINED_TERM_CROSS_CLAUSE"
    INDEPENDENT_COVENANT = "INDEPENDENT_COMMUTATIVE_COVENANT"


class CaseType(str, Enum):
    POSITIVE = "POSITIVE"
    HARD_NEGATIVE = "HARD_NEGATIVE"
    AMBIGUOUS = "AMBIGUOUS"


class LabelStatus(str, Enum):
    VERIFIED_POSITIVE = "VERIFIED_POSITIVE"
    VERIFIED_NEGATIVE = "VERIFIED_NEGATIVE"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID_TRANSFORMATION = "INVALID_TRANSFORMATION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EXPERT_ADJUDICATION_REQUIRED = "EXPERT_ADJUDICATION_REQUIRED"


class GranularityLevel(str, Enum):
    CLAUSE_LEVEL = "CLAUSE_LEVEL"
    PARAGRAPH_LEVEL = "PARAGRAPH_LEVEL"
    SENTENCE_LEVEL = "SENTENCE_LEVEL"


@dataclass
class DependencyCandidate:
    candidate_id: str
    parent_document_id: str
    document_family_id: str
    referencing_clause_id: str
    referencing_clause_idx: int
    referencing_char_start: int
    referencing_char_end: int
    referencing_text: str
    antecedent_clause_id: str
    antecedent_clause_idx: int
    antecedent_char_start: int
    antecedent_char_end: int
    antecedent_text: str
    dependency_class: DependencyClass
    is_intra_clause: bool
    is_cross_clause: bool
    directional_marker: str
    interpretation_if_inverted: str


@dataclass
class AntecedentResolutionRecord:
    candidate_id: str
    parent_document_id: str
    referencing_span: str
    resolved_antecedent_span: str
    resolution_method: str
    locality: str
    spans_clause_boundaries: bool
    alternative_antecedents_exist: bool
    confidence: str
    resolution_verdict: str


@dataclass
class DependencyBenchmarkCase:
    case_id: str
    parent_document_id: str
    document_family_id: str
    split_assignment: str
    case_type: CaseType
    dependency_class: DependencyClass
    granularity: GranularityLevel
    referencing_clause_id: str
    antecedent_clause_id: str
    referencing_text_span: str
    antecedent_text_span: str
    transformation_type: str
    original_clause_sequence: List[str]
    perturbed_clause_sequence: List[str]
    displaced_clause_idx: int
    target_clause_idx: int
    ground_truth_label: LabelStatus
    verification_status: str
    broken_relationship_explanation: str
    source_text_hash: str
    perturbed_text_hash: str
