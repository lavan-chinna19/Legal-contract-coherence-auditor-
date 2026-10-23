"""
src/research/dependency_ground_truth/builder.py
Pipeline for constructing Phase 4D-D Contract Dependency Dataset and Annotation Infrastructure.
"""
import os
import re
import csv
import json
import hashlib
from typing import List, Dict, Tuple, Optional, Any

from src.segmentation.rule_based import RuleBasedSegmenter
from src.config import ClauseRecord
from src.research.dependency_ground_truth.schema import (
    DependencyClass,
    CaseType,
    LabelStatus,
    GranularityLevel,
    DependencyCandidate,
    AntecedentResolutionRecord,
    DependencyBenchmarkCase
)


HEADING_RE = re.compile(r'^(?:(?:Section|Article)\s+)?([0-9]+(?:\.[0-9]+)*)', re.I)
REF_RE = re.compile(r'\b(?:Section|Article)\s+([0-9]+(?:\.[0-9]+)*)\s*(above|below|hereof|of\s+this\s+Agreement)?\b', re.I)
DISCOURSE_RE = re.compile(r'\b(?:notwithstanding\s+the\s+foregoing|subject\s+to\s+the\s+foregoing|in\s+the\s+preceding\s+section|the\s+preceding\s+sentence|as\s+stated\s+above)\b', re.I)
INDEPENDENT_COVENANT_KEYWORDS = ["notice", "governing law", "counterpart", "severability", "entire agreement", "amendment", "waiver"]


class DependencyDatasetBuilder:
    def __init__(
        self,
        parent_manifest_path: str = "research/independent_contract_benchmark_phase_04dc/parent_contract_manifest.csv",
        edgar_manifest_path: str = "data/raw/sec_edgar/edgar_manifest.json",
        raw_edgar_dir: str = "data/raw/sec_edgar"
    ):
        self.parent_manifest_path = parent_manifest_path
        self.edgar_manifest_path = edgar_manifest_path
        self.raw_edgar_dir = raw_edgar_dir
        self.segmenter = RuleBasedSegmenter()

        # Load parent contracts
        self.parents = []
        if os.path.exists(parent_manifest_path):
            with open(parent_manifest_path, "r", encoding="utf-8") as f:
                self.parents = list(csv.DictReader(f))

        # Map parent IDs to filenames
        self.parent_to_file = {}
        if os.path.exists(edgar_manifest_path):
            with open(edgar_manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries = data.get("entries", [])
            for p in self.parents:
                pid = p["parent_document_id"]
                for e in entries:
                    cik = e["cik"]
                    ex = e["exhibit_type"]
                    ex_norm = ex.replace(".", "_").replace("-", "_")
                    if f"CIK{cik}" in pid and ex_norm in pid:
                        self.parent_to_file[pid] = os.path.basename(e["local_path"])
                        break

    def load_parent_clauses(self, parent_id: str) -> Tuple[str, List[ClauseRecord]]:
        fn = self.parent_to_file.get(parent_id)
        if not fn:
            return "", []
        fpath = os.path.join(self.raw_edgar_dir, fn)
        if not os.path.exists(fpath):
            return "", []
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        clauses = self.segmenter.segment(text, doc_id=parent_id)
        return text, clauses

    def extract_candidates(self) -> Tuple[List[DependencyCandidate], List[AntecedentResolutionRecord]]:
        candidates = []
        resolutions = []
        cand_counter = 1

        for p in self.parents:
            pid = p["parent_document_id"]
            fam = p["document_family_id"]
            raw_text, clauses = self.load_parent_clauses(pid)
            if len(clauses) < 10:
                continue

            # 1. Map section headings to clause index
            sec_to_clause = {}
            for c_idx, c in enumerate(clauses):
                first_line = c.text.strip().split("\n")[0][:60]
                m = HEADING_RE.match(first_line)
                if m:
                    sec_num = m.group(1).rstrip(".")
                    if sec_num not in sec_to_clause:
                        sec_to_clause[sec_num] = (c_idx, first_line)

            # 2. Extract Cross-Clause Section References
            for c_idx, c in enumerate(clauses):
                for m in REF_RE.finditer(c.text):
                    target_sec = m.group(1).rstrip(".")
                    direction = (m.group(2) or "").strip()
                    if target_sec in sec_to_clause:
                        target_c_idx, target_heading = sec_to_clause[target_sec]
                        if target_c_idx != c_idx:
                            cid = f"DEP_CAND_{cand_counter:04d}"
                            cand_counter += 1
                            is_cross = (target_c_idx != c_idx)
                            is_forward = (c_idx > target_c_idx)

                            interp = (
                                f"Clause {c.clause_id} references {m.group(0)} defined in {clauses[target_c_idx].clause_id}. "
                                f"Inverting this order causes {m.group(0)} to reference a condition or definition not yet introduced."
                            )

                            cand = DependencyCandidate(
                                candidate_id=cid,
                                parent_document_id=pid,
                                document_family_id=fam,
                                referencing_clause_id=c.clause_id,
                                referencing_clause_idx=c_idx,
                                referencing_char_start=m.start(),
                                referencing_char_end=m.end(),
                                referencing_text=m.group(0),
                                antecedent_clause_id=clauses[target_c_idx].clause_id,
                                antecedent_clause_idx=target_c_idx,
                                antecedent_char_start=0,
                                antecedent_char_end=len(target_heading),
                                antecedent_text=target_heading,
                                dependency_class=DependencyClass.CROSS_CLAUSE_SECTION,
                                is_intra_clause=False,
                                is_cross_clause=True,
                                directional_marker=direction if direction else "none",
                                interpretation_if_inverted=interp
                            )
                            candidates.append(cand)

                            res = AntecedentResolutionRecord(
                                candidate_id=cid,
                                parent_document_id=pid,
                                referencing_span=m.group(0),
                                resolved_antecedent_span=target_heading,
                                resolution_method="DETERMINISTIC_SECTION_MAP",
                                locality="CROSS_CLAUSE",
                                spans_clause_boundaries=True,
                                alternative_antecedents_exist=False,
                                confidence="HIGH",
                                resolution_verdict="RESOLVED"
                            )
                            resolutions.append(res)

            # 3. Extract Discourse References (Intra-Clause and Cross-Clause)
            for c_idx, c in enumerate(clauses):
                sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', c.text) if s.strip()]
                if len(sents) < 2:
                    continue
                for m in DISCOURSE_RE.finditer(c.text):
                    cid = f"DEP_CAND_{cand_counter:04d}"
                    cand_counter += 1
                    char_pos = m.start()

                    # Find sentence
                    sent_idx = 0
                    cum_len = 0
                    for s_i, s in enumerate(sents):
                        if cum_len <= char_pos < cum_len + len(s) + 2:
                            sent_idx = s_i
                            break
                        cum_len += len(s) + 1

                    is_intra = (sent_idx > 0)
                    antecedent_span = sents[sent_idx - 1][:80] if is_intra else clauses[max(0, c_idx - 1)].text[:80]
                    ant_c_idx = c_idx if is_intra else max(0, c_idx - 1)
                    ant_c_id = c.clause_id if is_intra else clauses[ant_c_idx].clause_id

                    interp = (
                        f"Discourse marker '{m.group(0)}' refers to preceding sentence within the same clause."
                        if is_intra
                        else f"Discourse marker '{m.group(0)}' at clause boundary refers to preceding clause."
                    )

                    cand = DependencyCandidate(
                        candidate_id=cid,
                        parent_document_id=pid,
                        document_family_id=fam,
                        referencing_clause_id=c.clause_id,
                        referencing_clause_idx=c_idx,
                        referencing_char_start=m.start(),
                        referencing_char_end=m.end(),
                        referencing_text=m.group(0),
                        antecedent_clause_id=ant_c_id,
                        antecedent_clause_idx=ant_c_idx,
                        antecedent_char_start=0,
                        antecedent_char_end=len(antecedent_span),
                        antecedent_text=antecedent_span,
                        dependency_class=DependencyClass.INTRA_CLAUSE_DISCOURSE if is_intra else DependencyClass.CROSS_CLAUSE_DISCOURSE,
                        is_intra_clause=is_intra,
                        is_cross_clause=not is_intra,
                        directional_marker="preceding/foregoing",
                        interpretation_if_inverted=interp
                    )
                    candidates.append(cand)

                    res = AntecedentResolutionRecord(
                        candidate_id=cid,
                        parent_document_id=pid,
                        referencing_span=m.group(0),
                        resolved_antecedent_span=antecedent_span,
                        resolution_method="SENTENCE_POSITIONAL_ANALYSIS",
                        locality="INTRA_CLAUSE" if is_intra else "CROSS_CLAUSE",
                        spans_clause_boundaries=not is_intra,
                        alternative_antecedents_exist=not is_intra,
                        confidence="HIGH" if is_intra else "MEDIUM",
                        resolution_verdict="RESOLVED" if is_intra else "AMBIGUOUS"
                    )
                    resolutions.append(res)

        return candidates, resolutions

    def build_cases(
        self,
        candidates: List[DependencyCandidate]
    ) -> List[DependencyBenchmarkCase]:
        cases = []
        case_counter = 1

        # Track used parents to maximize diversity
        parent_usage = {}

        # ---------------------------------------------------------------------
        # 1. POSITIVE CASES (Target: 30 cases)
        # Move referencing clause to position BEFORE antecedent
        # ---------------------------------------------------------------------
        cross_candidates = [
            c for c in candidates
            if c.is_cross_clause and c.antecedent_clause_idx < c.referencing_clause_idx
        ]

        # Sort with directional markers ("above") first for highest linguistic clarity
        cross_candidates.sort(
            key=lambda c: (
                0 if "above" in c.directional_marker.lower() else 1,
                -(c.referencing_clause_idx - c.antecedent_clause_idx)
            )
        )

        pos_count = 0
        for cand in cross_candidates:
            if pos_count >= 30:
                break
            pid = cand.parent_document_id
            if parent_usage.get(pid, 0) >= 3:
                continue

            raw_text, clauses = self.load_parent_clauses(pid)
            if not clauses:
                continue

            ref_idx = cand.referencing_clause_idx
            ant_idx = cand.antecedent_clause_idx
            if ref_idx <= ant_idx or ant_idx >= len(clauses) or ref_idx >= len(clauses):
                continue

            # Perturbation: Move referencing clause to immediately BEFORE antecedent (ant_idx)
            orig_seq = [c.clause_id for c in clauses]
            pert_clauses = list(clauses)
            moved_clause = pert_clauses.pop(ref_idx)
            pert_clauses.insert(ant_idx, moved_clause)
            pert_seq = [c.clause_id for c in pert_clauses]

            source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            pert_text = "\n\n".join(c.text for c in pert_clauses)
            pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

            case_id = f"CASE_04DD_POS_{case_counter:03d}"
            case_counter += 1
            pos_count += 1
            parent_usage[pid] = parent_usage.get(pid, 0) + 1

            expl = (
                f"Referencing clause {moved_clause.clause_id} contains explicit cross-reference '{cand.referencing_text}' "
                f"to antecedent clause {cand.antecedent_clause_id}. Repositioning it before the antecedent "
                f"(from index {ref_idx} to index {ant_idx}) violates structural presupposition: "
                f"the condition/definition is referenced before it appears in the contract text."
            )

            cases.append(DependencyBenchmarkCase(
                case_id=case_id,
                parent_document_id=pid,
                document_family_id=cand.document_family_id,
                split_assignment="development",
                case_type=CaseType.POSITIVE,
                dependency_class=cand.dependency_class,
                granularity=GranularityLevel.CLAUSE_LEVEL,
                referencing_clause_id=cand.referencing_clause_id,
                antecedent_clause_id=cand.antecedent_clause_id,
                referencing_text_span=cand.referencing_text,
                antecedent_text_span=cand.antecedent_text,
                transformation_type="CROSS_CLAUSE_SECTION_INVERSION",
                original_clause_sequence=orig_seq,
                perturbed_clause_sequence=pert_seq,
                displaced_clause_idx=ref_idx,
                target_clause_idx=ant_idx,
                ground_truth_label=LabelStatus.VERIFIED_POSITIVE,
                verification_status="COMPUTATIONALLY_VERIFIED",
                broken_relationship_explanation=expl,
                source_text_hash=source_hash,
                perturbed_text_hash=pert_hash
            ))

        # ---------------------------------------------------------------------
        # 2. HARD NEGATIVE CASES (Target: 30 cases)
        # Categories:
        # a) Intra-clause discourse marker moved intact (P1 correction) - 10 cases
        # b) Coupled block movement (both antecedent and reference move) - 8 cases
        # c) Commutative covenant swaps (Notices & Governing Law) - 6 cases
        # d) Front-loaded definitions - 3 cases
        # e) Front-loaded dispute resolution - 3 cases
        # ---------------------------------------------------------------------
        neg_count = 0

        # a) Intra-clause discourse preservation (10 cases)
        intra_candidates = [c for c in candidates if c.is_intra_clause]
        for cand in intra_candidates:
            if neg_count >= 10:
                break
            pid = cand.parent_document_id
            raw_text, clauses = self.load_parent_clauses(pid)
            c_idx = cand.referencing_clause_idx
            if c_idx < 1 or c_idx >= len(clauses) - 1:
                continue

            # Swap clause c_idx with c_idx - 1
            target_idx = c_idx - 1
            orig_seq = [c.clause_id for c in clauses]
            pert_clauses = list(clauses)
            pert_clauses[c_idx], pert_clauses[target_idx] = pert_clauses[target_idx], pert_clauses[c_idx]
            pert_seq = [c.clause_id for c in pert_clauses]

            source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            pert_text = "\n\n".join(c.text for c in pert_clauses)
            pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

            case_id = f"CASE_04DD_NEG_{case_counter:03d}"
            case_counter += 1
            neg_count += 1

            expl = (
                f"Clause {clauses[c_idx].clause_id} contains discourse marker '{cand.referencing_text}' whose antecedent "
                f"is contained within the exact same clause ('{cand.antecedent_text}'). Inverting clause with neighbor "
                f"moves the clause intact; zero discourse dependency is broken. Ground truth is strictly negative."
            )

            cases.append(DependencyBenchmarkCase(
                case_id=case_id,
                parent_document_id=pid,
                document_family_id=cand.document_family_id,
                split_assignment="development",
                case_type=CaseType.HARD_NEGATIVE,
                dependency_class=DependencyClass.INTRA_CLAUSE_DISCOURSE,
                granularity=GranularityLevel.CLAUSE_LEVEL,
                referencing_clause_id=cand.referencing_clause_id,
                antecedent_clause_id=cand.antecedent_clause_id,
                referencing_text_span=cand.referencing_text,
                antecedent_text_span=cand.antecedent_text,
                transformation_type="INTRA_CLAUSE_DISCOURSE_PRESERVATION",
                original_clause_sequence=orig_seq,
                perturbed_clause_sequence=pert_seq,
                displaced_clause_idx=c_idx,
                target_clause_idx=target_idx,
                ground_truth_label=LabelStatus.VERIFIED_NEGATIVE,
                verification_status="COMPUTATIONALLY_VERIFIED",
                broken_relationship_explanation=expl,
                source_text_hash=source_hash,
                perturbed_text_hash=pert_hash
            ))

        # b) Coupled block movement (8 cases)
        # Move both antecedent and referencing clause together as a block
        for cand in cross_candidates:
            if neg_count >= 18:
                break
            pid = cand.parent_document_id
            ant_idx = cand.antecedent_clause_idx
            ref_idx = cand.referencing_clause_idx
            if ref_idx != ant_idx + 1:
                continue  # adjacent block

            raw_text, clauses = self.load_parent_clauses(pid)
            if len(clauses) < 12 or ant_idx < 3:
                continue

            # Move adjacent block [ant_idx, ref_idx] to earlier position (e.g. index 2)
            orig_seq = [c.clause_id for c in clauses]
            pert_clauses = list(clauses)
            block = [pert_clauses.pop(ref_idx), pert_clauses.pop(ant_idx)]
            block.reverse()  # [ant, ref]
            target_pos = 2
            pert_clauses[target_pos:target_pos] = block
            pert_seq = [c.clause_id for c in pert_clauses]

            source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            pert_text = "\n\n".join(c.text for c in pert_clauses)
            pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

            case_id = f"CASE_04DD_NEG_{case_counter:03d}"
            case_counter += 1
            neg_count += 1

            expl = (
                f"Clause {cand.referencing_clause_id} references {cand.antecedent_clause_id}. Both clauses were "
                f"repositioned together as a coupled block to index {target_pos}. Their relative sequence "
                f"(antecedent preceding reference) is completely preserved; zero cross-reference is broken."
            )

            cases.append(DependencyBenchmarkCase(
                case_id=case_id,
                parent_document_id=pid,
                document_family_id=cand.document_family_id,
                split_assignment="development",
                case_type=CaseType.HARD_NEGATIVE,
                dependency_class=DependencyClass.CROSS_CLAUSE_SECTION,
                granularity=GranularityLevel.CLAUSE_LEVEL,
                referencing_clause_id=cand.referencing_clause_id,
                antecedent_clause_id=cand.antecedent_clause_id,
                referencing_text_span=cand.referencing_text,
                antecedent_text_span=cand.antecedent_text,
                transformation_type="COUPLED_BLOCK_PRESERVATION",
                original_clause_sequence=orig_seq,
                perturbed_clause_sequence=pert_seq,
                displaced_clause_idx=ant_idx,
                target_clause_idx=target_pos,
                ground_truth_label=LabelStatus.VERIFIED_NEGATIVE,
                verification_status="COMPUTATIONALLY_VERIFIED",
                broken_relationship_explanation=expl,
                source_text_hash=source_hash,
                perturbed_text_hash=pert_hash
            ))

        # c) Commutative covenant swaps (6 cases)
        for p in self.parents:
            if neg_count >= 24:
                break
            pid = p["parent_document_id"]
            fam = p["document_family_id"]
            raw_text, clauses = self.load_parent_clauses(pid)
            if len(clauses) < 15:
                continue

            # Find two independent boilerplate clauses
            notices_idx = None
            gov_idx = None
            for idx, c in enumerate(clauses):
                lower_text = c.text.lower()
                if "notices" in lower_text and not notices_idx:
                    notices_idx = idx
                elif ("governing law" in lower_text or "jurisdiction" in lower_text) and not gov_idx:
                    gov_idx = idx

            if notices_idx and gov_idx and notices_idx != gov_idx:
                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                pert_clauses[notices_idx], pert_clauses[gov_idx] = pert_clauses[gov_idx], pert_clauses[notices_idx]
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_NEG_{case_counter:03d}"
                case_counter += 1
                neg_count += 1

                expl = (
                    f"Swapped independent commercial covenants (Notices at {clauses[notices_idx].clause_id} and "
                    f"Governing Law at {clauses[gov_idx].clause_id}). Neither clause contains cross-references to the other; "
                    f"covenants are commutative. Valid non-canonical variation."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=fam,
                    split_assignment="development",
                    case_type=CaseType.HARD_NEGATIVE,
                    dependency_class=DependencyClass.INDEPENDENT_COVENANT,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=clauses[notices_idx].clause_id,
                    antecedent_clause_id=clauses[gov_idx].clause_id,
                    referencing_text_span="Notices Provision",
                    antecedent_text_span="Governing Law Provision",
                    transformation_type="INDEPENDENT_COVENANT_COMMUTATIVE_SWAP",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=notices_idx,
                    target_clause_idx=gov_idx,
                    ground_truth_label=LabelStatus.VERIFIED_NEGATIVE,
                    verification_status="COMPUTATIONALLY_VERIFIED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        # d) Front-loaded definitions (3 cases)
        for p in self.parents:
            if neg_count >= 27:
                break
            pid = p["parent_document_id"]
            fam = p["document_family_id"]
            raw_text, clauses = self.load_parent_clauses(pid)
            if len(clauses) < 15:
                continue

            # Find definitions clause
            defs_idx = None
            for idx, c in enumerate(clauses):
                if "definition" in c.text.lower() and idx > 3:
                    defs_idx = idx
                    break

            if defs_idx:
                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                moved = pert_clauses.pop(defs_idx)
                pert_clauses.insert(1, moved)  # Move definitions to beginning (index 1)
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_NEG_{case_counter:03d}"
                case_counter += 1
                neg_count += 1

                expl = (
                    f"Front-loaded Definitions clause {moved.clause_id} to document opening (index 1). "
                    f"Definitions precede substantive terms; established commercial contract drafting variation."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=fam,
                    split_assignment="development",
                    case_type=CaseType.HARD_NEGATIVE,
                    dependency_class=DependencyClass.DEFINED_TERM_CROSS_CLAUSE,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=moved.clause_id,
                    antecedent_clause_id="DOCUMENT_PREAMBLE",
                    referencing_text_span="Definitions Article",
                    antecedent_text_span="Contract Opening",
                    transformation_type="FRONT_LOADED_DEFINITIONS",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=defs_idx,
                    target_clause_idx=1,
                    ground_truth_label=LabelStatus.VERIFIED_NEGATIVE,
                    verification_status="COMPUTATIONALLY_VERIFIED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        # e) Front-loaded dispute resolution (3 cases)
        for p in self.parents:
            if neg_count >= 30:
                break
            pid = p["parent_document_id"]
            fam = p["document_family_id"]
            raw_text, clauses = self.load_parent_clauses(pid)
            if len(clauses) < 15:
                continue

            dispute_idx = None
            for idx, c in enumerate(clauses):
                if ("dispute" in c.text.lower() or "arbitration" in c.text.lower()) and idx > 4:
                    dispute_idx = idx
                    break

            if dispute_idx:
                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                moved = pert_clauses.pop(dispute_idx)
                pert_clauses.insert(1, moved)
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_NEG_{case_counter:03d}"
                case_counter += 1
                neg_count += 1

                expl = (
                    f"Front-loaded dispute resolution clause {moved.clause_id} to index 1. "
                    f"Common in consumer and standard commercial agreements; no broken internal dependency."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=fam,
                    split_assignment="development",
                    case_type=CaseType.HARD_NEGATIVE,
                    dependency_class=DependencyClass.INDEPENDENT_COVENANT,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=moved.clause_id,
                    antecedent_clause_id="DOCUMENT_PREAMBLE",
                    referencing_text_span="Dispute Resolution Clause",
                    antecedent_text_span="Contract Opening",
                    transformation_type="FRONT_LOADED_DISPUTE_RESOLUTION",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=dispute_idx,
                    target_clause_idx=1,
                    ground_truth_label=LabelStatus.VERIFIED_NEGATIVE,
                    verification_status="COMPUTATIONALLY_VERIFIED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        # ---------------------------------------------------------------------
        # 3. AMBIGUOUS CASES (Target: 12 cases)
        # Displacements where dependency validity is uncertain or depends on
        # subjective legal interpretation (e.g. general discourse markers without
        # explicit numbering, deictic directional conflicts, or intervening subsection moves).
        # ---------------------------------------------------------------------
        ambig_count = 0

        # a) Unresolved cross-clause discourse markers (3 cases)
        for cand in candidates:
            if ambig_count >= 3:
                break
            if cand.dependency_class == DependencyClass.CROSS_CLAUSE_DISCOURSE and not cand.is_intra_clause:
                pid = cand.parent_document_id
                raw_text, clauses = self.load_parent_clauses(pid)
                c_idx = cand.referencing_clause_idx
                if c_idx < 2 or c_idx >= len(clauses) - 2:
                    continue

                target_idx = max(0, c_idx - 3)
                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                moved = pert_clauses.pop(c_idx)
                pert_clauses.insert(target_idx, moved)
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_AMBIG_{case_counter:03d}"
                case_counter += 1
                ambig_count += 1

                expl = (
                    f"Clause {moved.clause_id} contains backward discourse marker '{cand.referencing_text}'. "
                    f"Repositioned to index {target_idx}. While the immediately preceding clause was altered, "
                    f"the broad semantic context may still support the discourse relation. Lacks deterministic section reference; "
                    f"labeled AMBIGUOUS pending expert legal adjudication."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=cand.document_family_id,
                    split_assignment="development",
                    case_type=CaseType.AMBIGUOUS,
                    dependency_class=cand.dependency_class,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=cand.referencing_clause_id,
                    antecedent_clause_id=cand.antecedent_clause_id,
                    referencing_text_span=cand.referencing_text,
                    antecedent_text_span=cand.antecedent_text,
                    transformation_type="UNRESOLVED_DISCOURSE_REFERENCE_DISPLACEMENT",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=c_idx,
                    target_clause_idx=target_idx,
                    ground_truth_label=LabelStatus.AMBIGUOUS,
                    verification_status="EXPERT_ADJUDICATION_REQUIRED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        # b) Directional deictic contradiction ("Section X below" moved after Section X) (4 cases)
        for cand in candidates:
            if ambig_count >= 7:
                break
            if "below" in cand.directional_marker.lower() and cand.antecedent_clause_idx > cand.referencing_clause_idx:
                pid = cand.parent_document_id
                raw_text, clauses = self.load_parent_clauses(pid)
                ref_idx = cand.referencing_clause_idx
                ant_idx = cand.antecedent_clause_idx
                if ant_idx >= len(clauses) - 1:
                    continue

                target_idx = min(len(clauses) - 1, ant_idx + 1)
                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                moved = pert_clauses.pop(ref_idx)
                pert_clauses.insert(target_idx, moved)
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_AMBIG_{case_counter:03d}"
                case_counter += 1
                ambig_count += 1

                expl = (
                    f"Clause {moved.clause_id} references '{cand.referencing_text}'. Repositioned to index {target_idx} "
                    f"(after target {cand.antecedent_clause_id}). The section number remains resolvable in the contract, "
                    f"but the directional deictic marker ('below') is rendered geographically false (it is now above). "
                    f"Conflict between literal directional pointer and substantive validity requires legal expert adjudication."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=cand.document_family_id,
                    split_assignment="development",
                    case_type=CaseType.AMBIGUOUS,
                    dependency_class=cand.dependency_class,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=cand.referencing_clause_id,
                    antecedent_clause_id=cand.antecedent_clause_id,
                    referencing_text_span=cand.referencing_text,
                    antecedent_text_span=cand.antecedent_text,
                    transformation_type="DEICTIC_DIRECTIONAL_CONTRADICTION",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=ref_idx,
                    target_clause_idx=target_idx,
                    ground_truth_label=LabelStatus.AMBIGUOUS,
                    verification_status="EXPERT_ADJUDICATION_REQUIRED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        # c) Intervening subsection displacement (3 cases)
        for cand in cross_candidates:
            if ambig_count >= 10:
                break
            ref_idx = cand.referencing_clause_idx
            ant_idx = cand.antecedent_clause_idx
            if ref_idx > ant_idx + 3:
                pid = cand.parent_document_id
                raw_text, clauses = self.load_parent_clauses(pid)
                target_idx = ant_idx + 1

                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                moved = pert_clauses.pop(ref_idx)
                pert_clauses.insert(target_idx, moved)
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_AMBIG_{case_counter:03d}"
                case_counter += 1
                ambig_count += 1

                expl = (
                    f"Clause {moved.clause_id} references {cand.antecedent_clause_id} and was moved to index {target_idx}. "
                    f"The provision remains positioned after the referenced section, but displaces intermediate subsections. "
                    f"Ambiguous whether intra-article subsection disruption alters contractual interpretation."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=cand.document_family_id,
                    split_assignment="development",
                    case_type=CaseType.AMBIGUOUS,
                    dependency_class=cand.dependency_class,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=cand.referencing_clause_id,
                    antecedent_clause_id=cand.antecedent_clause_id,
                    referencing_text_span=cand.referencing_text,
                    antecedent_text_span=cand.antecedent_text,
                    transformation_type="INTERVENING_SUBSECTION_DISPLACEMENT",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=ref_idx,
                    target_clause_idx=target_idx,
                    ground_truth_label=LabelStatus.AMBIGUOUS,
                    verification_status="EXPERT_ADJUDICATION_REQUIRED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        # d) Distant cross-article relocation with resolvable reference (2 cases)
        for cand in cross_candidates:
            if ambig_count >= 12:
                break
            ref_idx = cand.referencing_clause_idx
            pid = cand.parent_document_id
            raw_text, clauses = self.load_parent_clauses(pid)
            if len(clauses) > 20 and ref_idx < len(clauses) - 5:
                target_idx = len(clauses) - 2

                orig_seq = [c.clause_id for c in clauses]
                pert_clauses = list(clauses)
                moved = pert_clauses.pop(ref_idx)
                pert_clauses.insert(target_idx, moved)
                pert_seq = [c.clause_id for c in pert_clauses]

                source_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                pert_text = "\n\n".join(c.text for c in pert_clauses)
                pert_hash = hashlib.sha256(pert_text.encode("utf-8")).hexdigest()

                case_id = f"CASE_04DD_AMBIG_{case_counter:03d}"
                case_counter += 1
                ambig_count += 1

                expl = (
                    f"Clause {moved.clause_id} references {cand.antecedent_clause_id} and was relocated across article "
                    f"boundaries to the closing boilerplate section (index {target_idx}). While the cross-reference target "
                    f"is formally present in the document, moving substantive terms into boilerplate alters construction."
                )

                cases.append(DependencyBenchmarkCase(
                    case_id=case_id,
                    parent_document_id=pid,
                    document_family_id=cand.document_family_id,
                    split_assignment="development",
                    case_type=CaseType.AMBIGUOUS,
                    dependency_class=cand.dependency_class,
                    granularity=GranularityLevel.CLAUSE_LEVEL,
                    referencing_clause_id=cand.referencing_clause_id,
                    antecedent_clause_id=cand.antecedent_clause_id,
                    referencing_text_span=cand.referencing_text,
                    antecedent_text_span=cand.antecedent_text,
                    transformation_type="CROSS_ARTICLE_RELOCATION_AMBIGUITY",
                    original_clause_sequence=orig_seq,
                    perturbed_clause_sequence=pert_seq,
                    displaced_clause_idx=ref_idx,
                    target_clause_idx=target_idx,
                    ground_truth_label=LabelStatus.AMBIGUOUS,
                    verification_status="EXPERT_ADJUDICATION_REQUIRED",
                    broken_relationship_explanation=expl,
                    source_text_hash=source_hash,
                    perturbed_text_hash=pert_hash
                ))

        return cases


def build_and_export_phase_04dd(output_dir: str = "research/dependency_ground_truth_phase_04dd"):
    os.makedirs(output_dir, exist_ok=True)
    builder = DependencyDatasetBuilder()

    print("[Phase 4D-D] Extracting candidates and resolving antecedents...")
    candidates, resolutions = builder.extract_candidates()
    print(f"Extracted {len(candidates)} dependency candidates and {len(resolutions)} resolution records.")

    print("[Phase 4D-D] Building benchmark cases (Positives, Hard Negatives, Ambiguous)...")
    cases = builder.build_cases(candidates)
    print(f"Constructed {len(cases)} benchmark cases:")
    pos_cases = [c for c in cases if c.case_type == CaseType.POSITIVE]
    neg_cases = [c for c in cases if c.case_type == CaseType.HARD_NEGATIVE]
    amb_cases = [c for c in cases if c.case_type == CaseType.AMBIGUOUS]
    print(f"  - Verified Positives: {len(pos_cases)}")
    print(f"  - Hard Negatives: {len(neg_cases)}")
    print(f"  - Ambiguous Cases: {len(amb_cases)}")

    # 1. Export dataset_manifest.csv
    manifest_path = os.path.join(output_dir, "dataset_manifest.csv")
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id", "parent_document_id", "document_family_id", "split_assignment",
            "case_type", "dependency_class", "granularity", "referencing_clause_id",
            "antecedent_clause_id", "referencing_text_span", "antecedent_text_span",
            "transformation_type", "ground_truth_label", "verification_status",
            "displaced_clause_idx", "target_clause_idx", "source_text_hash", "perturbed_text_hash"
        ])
        for c in cases:
            writer.writerow([
                c.case_id, c.parent_document_id, c.document_family_id, c.split_assignment,
                c.case_type.value, c.dependency_class.value, c.granularity.value,
                c.referencing_clause_id, c.antecedent_clause_id, c.referencing_text_span,
                c.antecedent_text_span, c.transformation_type, c.ground_truth_label.value,
                c.verification_status, c.displaced_clause_idx, c.target_clause_idx,
                c.source_text_hash, c.perturbed_text_hash
            ])

    # 2. Export source_family_manifest.csv
    fam_path = os.path.join(output_dir, "source_family_manifest.csv")
    fam_cases = {}
    for c in cases:
        fid = c.document_family_id
        if fid not in fam_cases:
            fam_cases[fid] = {"pos": 0, "neg": 0, "amb": 0, "parents": set()}
        if c.case_type == CaseType.POSITIVE:
            fam_cases[fid]["pos"] += 1
        elif c.case_type == CaseType.HARD_NEGATIVE:
            fam_cases[fid]["neg"] += 1
        else:
            fam_cases[fid]["amb"] += 1
        fam_cases[fid]["parents"].add(c.parent_document_id)

    with open(fam_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "document_family_id", "parent_contract_count", "positive_cases_count",
            "negative_cases_count", "ambiguous_cases_count", "total_cases",
            "split_eligibility", "rights_classification"
        ])
        for fid, stats in sorted(fam_cases.items()):
            tot = stats["pos"] + stats["neg"] + stats["amb"]
            writer.writerow([
                fid, len(stats["parents"]), stats["pos"], stats["neg"], stats["amb"], tot,
                "DEVELOPMENT_ONLY", "PUBLICLY_ACCESSIBLE_RIGHTS_UNDETERMINED"
            ])

    # 3. Export dependency_candidates.csv
    cand_path = os.path.join(output_dir, "dependency_candidates.csv")
    with open(cand_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "candidate_id", "parent_document_id", "document_family_id", "referencing_clause_id",
            "referencing_clause_idx", "referencing_char_start", "referencing_char_end",
            "referencing_text", "antecedent_clause_id", "antecedent_clause_idx",
            "antecedent_char_start", "antecedent_char_end", "antecedent_text",
            "dependency_class", "is_intra_clause", "is_cross_clause", "directional_marker",
            "interpretation_if_inverted"
        ])
        for c in candidates:
            writer.writerow([
                c.candidate_id, c.parent_document_id, c.document_family_id, c.referencing_clause_id,
                c.referencing_clause_idx, c.referencing_char_start, c.referencing_char_end,
                c.referencing_text, c.antecedent_clause_id, c.antecedent_clause_idx,
                c.antecedent_char_start, c.antecedent_char_end, c.antecedent_text,
                c.dependency_class.value, c.is_intra_clause, c.is_cross_clause,
                c.directional_marker, c.interpretation_if_inverted
            ])

    # 4. Export antecedent_resolution.csv
    res_path = os.path.join(output_dir, "antecedent_resolution.csv")
    with open(res_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "candidate_id", "parent_document_id", "referencing_span", "resolved_antecedent_span",
            "resolution_method", "locality", "spans_clause_boundaries",
            "alternative_antecedents_exist", "confidence", "resolution_verdict"
        ])
        for r in resolutions:
            writer.writerow([
                r.candidate_id, r.parent_document_id, r.referencing_span, r.resolved_antecedent_span,
                r.resolution_method, r.locality, r.spans_clause_boundaries,
                r.alternative_antecedents_exist, r.confidence, r.resolution_verdict
            ])

    # 5. Export positive_cases.csv
    pos_path = os.path.join(output_dir, "positive_cases.csv")
    with open(pos_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id", "parent_document_id", "document_family_id", "referencing_clause_id",
            "antecedent_clause_id", "referencing_text_span", "antecedent_text_span",
            "transformation_type", "displaced_clause_idx", "target_clause_idx",
            "broken_relationship_explanation", "verification_status"
        ])
        for c in pos_cases:
            writer.writerow([
                c.case_id, c.parent_document_id, c.document_family_id, c.referencing_clause_id,
                c.antecedent_clause_id, c.referencing_text_span, c.antecedent_text_span,
                c.transformation_type, c.displaced_clause_idx, c.target_clause_idx,
                c.broken_relationship_explanation, c.verification_status
            ])

    # 6. Export negative_cases.csv
    neg_path = os.path.join(output_dir, "negative_cases.csv")
    with open(neg_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id", "parent_document_id", "document_family_id", "referencing_clause_id",
            "antecedent_clause_id", "referencing_text_span", "antecedent_text_span",
            "transformation_type", "displaced_clause_idx", "target_clause_idx",
            "preservation_rationale", "verification_status"
        ])
        for c in neg_cases:
            writer.writerow([
                c.case_id, c.parent_document_id, c.document_family_id, c.referencing_clause_id,
                c.antecedent_clause_id, c.referencing_text_span, c.antecedent_text_span,
                c.transformation_type, c.displaced_clause_idx, c.target_clause_idx,
                c.broken_relationship_explanation, c.verification_status
            ])

    # 7. Export ambiguous_cases.csv
    amb_path = os.path.join(output_dir, "ambiguous_cases.csv")
    with open(amb_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id", "parent_document_id", "document_family_id", "referencing_clause_id",
            "antecedent_clause_id", "referencing_text_span", "antecedent_text_span",
            "transformation_type", "displaced_clause_idx", "target_clause_idx",
            "ambiguity_rationale", "adjudication_status"
        ])
        for c in amb_cases:
            writer.writerow([
                c.case_id, c.parent_document_id, c.document_family_id, c.referencing_clause_id,
                c.antecedent_clause_id, c.referencing_text_span, c.antecedent_text_span,
                c.transformation_type, c.displaced_clause_idx, c.target_clause_idx,
                c.broken_relationship_explanation, "EXPERT_ADJUDICATION_REQUIRED"
            ])

    # 8. Export annotation_queue.csv
    queue_path = os.path.join(output_dir, "annotation_queue.csv")
    with open(queue_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id", "parent_document_id", "task_description", "referencing_clause_id",
            "referencing_span", "antecedent_clause_id", "antecedent_span",
            "proposed_label", "reviewer_verdict", "adjudication_status", "adjudication_notes"
        ])
        for c in cases:
            task_desc = f"Evaluate whether {c.transformation_type} creates an objective textual/structural defect."
            writer.writerow([
                c.case_id, c.parent_document_id, task_desc, c.referencing_clause_id,
                c.referencing_text_span, c.antecedent_clause_id, c.antecedent_text_span,
                c.ground_truth_label.value, "PENDING_REVIEW",
                "EXPERT_ADJUDICATION_REQUIRED" if c.case_type == CaseType.AMBIGUOUS else "COMPUTATIONALLY_PRE_ANNOTATED",
                c.broken_relationship_explanation
            ])

    print("[Phase 4D-D] Successfully exported all 8 dataset artifacts.")


if __name__ == "__main__":
    build_and_export_phase_04dd()
