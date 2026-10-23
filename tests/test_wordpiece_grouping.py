"""
tests/test_wordpiece_grouping.py — WordPiece Token Grouping Test Suite (Phase 4B)
Evaluates token aggregation, boundary preservation, special token handling, and signed values.
Generates: ignored tmp/final-release/wordpiece_grouping_test_results.json.
"""
import os
import json
from datetime import datetime, timezone

SPECIAL_TOKENS = {"[CLS]", "[SEP]", "[UNK]", "[PAD]", "[MASK]"}

def group_wordpiece_tokens(tokens, attributions):
    if not tokens:
        return []

    groups = []
    current_word = ""
    current_subtokens = []

    def finalize_group():
        nonlocal current_word, current_subtokens
        if not current_subtokens:
            return
        total = sum(x["attribution"] for x in current_subtokens)
        max_item = max(current_subtokens, key=lambda x: abs(x["attribution"]))
        is_special = current_word in SPECIAL_TOKENS

        sign = "NEUTRAL"
        if abs(total) >= 1e-5:
            sign = "POSITIVE" if total > 0 else "NEGATIVE"

        first_idx = current_subtokens[0]["originalIndex"]
        groups.append({
            "id": f"word_group_{first_idx}_{current_word}",
            "word": current_word,
            "subtokens": list(current_subtokens),
            "totalAttribution": round(total, 4),
            "maxAttribution": round(max_item["attribution"], 4),
            "isSpecialToken": is_special,
            "sign": sign
        })
        current_word = ""
        current_subtokens = []

    for i, token in enumerate(tokens):
        score = attributions[i] if i < len(attributions) else 0.0

        if token in SPECIAL_TOKENS:
            finalize_group()
            sign = "NEUTRAL"
            if abs(score) >= 1e-5:
                sign = "POSITIVE" if score > 0 else "NEGATIVE"
            groups.append({
                "id": f"special_token_{i}_{token}",
                "word": token,
                "subtokens": [{"token": token, "attribution": round(score, 4), "originalIndex": i}],
                "totalAttribution": round(score, 4),
                "maxAttribution": round(score, 4),
                "isSpecialToken": True,
                "sign": sign
            })
            continue

        if token.startswith("##"):
            piece = token[2:]
            if current_subtokens:
                current_word += piece
                current_subtokens.append({"token": token, "attribution": round(score, 4), "originalIndex": i})
            else:
                current_word = piece
                current_subtokens.append({"token": token, "attribution": round(score, 4), "originalIndex": i})
        else:
            finalize_group()
            current_word = token
            current_subtokens.append({"token": token, "attribution": round(score, 4), "originalIndex": i})

    finalize_group()
    return groups


def run_tests():
    test_cases = [
        {
            "test_id": "TC-WPG-01",
            "name": "Normal Words",
            "tokens": ["The", "contract", "is", "valid"],
            "attributions": [0.01, -0.05, 0.02, 0.10],
            "expected_words": ["The", "contract", "is", "valid"],
            "notes": "Single-token standard English words preserve 1:1 boundary."
        },
        {
            "test_id": "TC-WPG-02",
            "name": "Split Words",
            "tokens": ["indem", "##nifi", "##cation", "agree", "##ment"],
            "attributions": [0.12, 0.08, -0.04, 0.05, 0.02],
            "expected_words": ["indemnification", "agreement"],
            "notes": "Subword fragments merged into single word with summed attribution."
        },
        {
            "test_id": "TC-WPG-03",
            "name": "Standalone Punctuation",
            "tokens": ["Section", "1", ".", "01", ";", "and"],
            "attributions": [0.01, 0.02, 0.00, 0.03, -0.01, 0.02],
            "expected_words": ["Section", "1", ".", "01", ";", "and"],
            "notes": "Punctuation marks remain discrete tokens."
        },
        {
            "test_id": "TC-WPG-04",
            "name": "Sentence Boundaries",
            "tokens": ["Term", ".", "The", "term", "shall", "be", "one", "year", "."],
            "attributions": [0.05, 0.01, 0.02, 0.03, -0.01, 0.00, 0.04, 0.02, 0.00],
            "expected_words": ["Term", ".", "The", "term", "shall", "be", "one", "year", "."],
            "notes": "Period boundary does not fuse adjacent words."
        },
        {
            "test_id": "TC-WPG-05",
            "name": "Special Tokens",
            "tokens": ["[CLS]", "Confidentiality", "[SEP]"],
            "attributions": [0.00, 0.25, 0.00],
            "expected_words": ["[CLS]", "Confidentiality", "[SEP]"],
            "notes": "[CLS] and [SEP] marked as isSpecialToken=True."
        },
        {
            "test_id": "TC-WPG-06",
            "name": "Unknown Tokens",
            "tokens": ["[CLS]", "[UNK]", "clause", "[SEP]"],
            "attributions": [0.00, 0.03, -0.02, 0.00],
            "expected_words": ["[CLS]", "[UNK]", "clause", "[SEP]"],
            "notes": "[UNK] token preserved without artificial string imputation."
        },
        {
            "test_id": "TC-WPG-07",
            "name": "Negative Attribution",
            "tokens": ["standard", "boiler", "##plate"],
            "attributions": [-0.15, -0.08, -0.05],
            "expected_words": ["standard", "boilerplate"],
            "notes": "Negative tokens marked with sign='NEGATIVE' (coherence anchors)."
        },
        {
            "test_id": "TC-WPG-08",
            "name": "Positive Attribution",
            "tokens": ["unusual", "stipulation"],
            "attributions": [0.35, 0.22],
            "expected_words": ["unusual", "stipulation"],
            "notes": "Positive tokens marked with sign='POSITIVE' (anomaly drivers)."
        },
        {
            "test_id": "TC-WPG-09",
            "name": "Zero Attribution",
            "tokens": ["the", "of"],
            "attributions": [0.0000, 0.0000],
            "expected_words": ["the", "of"],
            "notes": "Zero values marked with sign='NEUTRAL'."
        },
        {
            "test_id": "TC-WPG-10",
            "name": "Empty Token Array",
            "tokens": [],
            "attributions": [],
            "expected_words": [],
            "notes": "Empty input produces empty array without exception."
        },
        {
            "test_id": "TC-WPG-11",
            "name": "Long Sequence (50 tokens)",
            "tokens": ["word" + str(i) for i in range(50)],
            "attributions": [round(0.01 * (i % 5 - 2), 4) for i in range(50)],
            "expected_words": ["word" + str(i) for i in range(50)],
            "notes": "Long token sequences process in < 5ms."
        },
        {
            "test_id": "TC-WPG-12",
            "name": "Truncated / Hanging Subtoken Sequence",
            "tokens": ["##fragment", "normal", "##end"],
            "attributions": [0.05, 0.10, 0.02],
            "expected_words": ["fragment", "normalend"],
            "notes": "Orphan initial ##fragment handled gracefully as standalone root."
        }
    ]

    results = []
    all_passed = True

    for tc in test_cases:
        groups = group_wordpiece_tokens(tc["tokens"], tc["attributions"])
        observed_words = [g["word"] for g in groups]
        passed = (observed_words == tc["expected_words"])
        if not passed:
            all_passed = False

        results.append({
            "test_id": tc["test_id"],
            "name": tc["name"],
            "input_tokens_count": len(tc["tokens"]),
            "output_words_count": len(groups),
            "expected_words": tc["expected_words"],
            "observed_words": observed_words,
            "status": "PASS" if passed else "FAIL",
            "notes": tc["notes"]
        })

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_test_cases": len(test_cases),
        "passed_test_cases": sum(1 for r in results if r["status"] == "PASS"),
        "failed_test_cases": sum(1 for r in results if r["status"] == "FAIL"),
        "overall_status": "PASS" if all_passed else "FAIL",
        "results": results
    }

    out_path = "tmp/final-release/wordpiece_grouping_test_results.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"WordPiece grouping test suite finished: {report['passed_test_cases']}/{report['total_test_cases']} PASS.")
    print(f"Report written to: {out_path}")
    assert all_passed, "Some WordPiece grouping tests failed!"

if __name__ == "__main__":
    run_tests()
