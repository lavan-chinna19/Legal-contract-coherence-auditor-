"""Experimental explicit-reference graph. No editorial-order or legal inference."""
import re

NUMBER = r"\d+(?:\.\d+)*(?:\([a-z0-9]+\))*"
DECLARATION = re.compile(rf"(?im)^[ \t]*(?:Section[ \t]+)?(?P<id>{NUMBER})(?:[.)]?[ \t]+|[.:]$)")
REFERENCE = re.compile(rf"\bSection\s+(?P<id>{NUMBER})(?!\w|\.\d)(?:\s+(?P<direction>above|below))?", re.I)


def detect_dependencies(clauses: list[dict]) -> dict:
    declarations, edges, findings, reviews = {}, [], [], []
    for index, clause in enumerate(clauses):
        for match in DECLARATION.finditer(clause["text"]):
            tail = clause["text"][match.end():]
            if re.match(r"(?i)(?:above|below|shall|is|applies|provides|states)\b", tail):
                continue
            identity = match["id"].lower()
            declarations.setdefault(identity, []).append({"clause_id": clause["clause_id"],
                "section_id": identity, "position": [index, match.start()], "excerpt": match.group(0).strip()})
    all_targets = sorted([target for targets in declarations.values() for target in targets], key=lambda t: t["position"])
    for index, clause in enumerate(clauses):
        for match in REFERENCE.finditer(clause["text"]):
            # A heading occurrence declares a target and is not a citation.
            if any(t["clause_id"] == clause["clause_id"] and t["position"][1] <= match.start() < t["position"][1] + len(t["excerpt"])
                   for t in declarations.get(match["id"].lower(), [])):
                continue
            direction = (match["direction"] or "").lower()
            prefix = clause["text"][max(0, match.start() - 28):match.start()].lower()
            if re.search(r"immediately\s+preceding\s*$", prefix):
                direction = "immediately_preceding"
            targets = declarations.get(match["id"].lower(), [])
            edge = {"source_clause_id": clause["clause_id"], "target_section_id": match["id"],
                    "reference": match.group(0), "char_start": match.start(), "char_end": match.end(),
                    "direction": direction or "nondirectional", "source_position": [index, match.start()]}
            if len(targets) != 1:
                edge.update(status="REVIEW_REQUIRED", reason="Unresolved or duplicate target; abstained.")
                reviews.append(edge)
            else:
                target = targets[0]
                edge["target"] = target
                valid = True
                if direction == "above":
                    valid = target["position"] < edge["source_position"]
                elif direction == "below":
                    valid = target["position"] > edge["source_position"]
                elif direction == "immediately_preceding":
                    source_headings = [t for t in all_targets if t["position"] <= edge["source_position"]]
                    current = source_headings[-1] if source_headings else None
                    preceding = all_targets[all_targets.index(current) - 1] if current and all_targets.index(current) > 0 else None
                    if current is None or preceding is None:
                        edge.update(status="REVIEW_REQUIRED", reason="Immediate predecessor cannot be uniquely established.")
                        reviews.append(edge)
                        edges.append(edge)
                        continue
                    valid = preceding is target
                edge["status"] = "SATISFIED" if valid else "VERIFIED_TEXTUAL_CONFLICT"
                edge["reason"] = "Explicit target location matches the reference." if valid else "Explicit directional reference contradicts the target's location."
                if not valid:
                    findings.append(edge)
            edges.append(edge)
        unsupported = re.finditer(r"\bSection\s+[IVXLCDM]+\b", clause["text"], re.I)
        for match in unsupported:
            reviews.append({"source_clause_id": clause["clause_id"], "reference": match.group(0),
                            "status": "REVIEW_REQUIRED", "reason": "Roman section identity is outside the supported numeric parser; abstained."})
        body = clause["text"]
        first_line, separator, remainder = body.partition("\n")
        if separator and DECLARATION.match(first_line):
            body = remainder
        vague = re.search(r"(?i)^\s*(?:notwithstanding\s+)?(?:the\s+)?(?:foregoing|preceding|above-mentioned)\b", body)
        if vague:
            reviews.append({"source_clause_id": clause["clause_id"], "reference": vague.group(0).strip(),
                            "status": "REVIEW_REQUIRED", "reason": "Boundary antecedent not explicit; no guessed dependency."})
    return {"experimental": True, "version": "explicit-dependency-graph-v1", "edges": edges,
            "findings": findings, "reviews": reviews,
            "status": "FINDING" if findings else "REVIEW_REQUIRED" if reviews else "NO_FINDINGS",
            "scope": "Deterministic textual direction only; independent scientific validation pending. Ensemble scores unchanged."}
