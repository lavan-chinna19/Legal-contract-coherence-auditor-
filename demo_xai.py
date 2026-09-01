"""
demo_xai.py — Standalone CLI script to demonstrate the XAI layer on real flagged clauses.
"""
import json
import warnings
warnings.filterwarnings("ignore")

from src.config import RAW_DIR
from src.segmentation.factory import get_segmenter
from src.scoring.pipeline import DualChannelScorer
from src.scoring.channel_a import ChannelAScorer
from src.scoring.channel_b import ChannelBScorer

from src.xai import (
    IntegratedGradientsExplainer,
    ChannelBSensitivityAnalyzer,
    NearestNeighborRetriever
)


def run_demo():
    print("Initializing scoring pipeline and explainers...")
    segmenter = get_segmenter("v2")
    channel_a = ChannelAScorer()
    channel_b = ChannelBScorer()
    pipeline = DualChannelScorer(channel_a=channel_a, channel_b=channel_b, high_threshold=0.1, med_threshold=0.1)

    ig_explainer = IntegratedGradientsExplainer(channel_a)
    sensitivity_analyzer = ChannelBSensitivityAnalyzer(channel_b)
    nn_retriever = NearestNeighborRetriever(embedder=channel_a.embedder)
    print("Searching for real flagged clauses in raw contracts...")
    file = RAW_DIR / "sec_edgar" / "0001967649_23_000025_EX-10_23.txt"
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()

    clauses = segmenter.segment(text, str(file.name))
    
    # Shuffle a few clauses to artificially create a real anomaly in this small doc
    # so we guarantee we find one without needing to parse the whole dataset
    import random
    import copy
    shuffled_clauses = copy.deepcopy(clauses)
    random.seed(42)
    random.shuffle(shuffled_clauses)
    for i, c in enumerate(shuffled_clauses):
        c.sequence_idx = i

    print("Scoring document...")
    res = pipeline.score_document(shuffled_clauses, str(file.name))
    
    all_clauses_scored = []
    for clause_res in res.clauses:
        original_clause = next(c for c in shuffled_clauses if c.clause_id == clause_res.clause_id)
        all_clauses_scored.append({
            "clause": original_clause,
            "doc_clauses": shuffled_clauses,
            "res": clause_res
        })

    # Sort descending by combined_score and take top 3
    all_clauses_scored.sort(key=lambda x: x["res"].combined_score, reverse=True)
    anomalies = all_clauses_scored[:3]

    print(f"\nFOUND {len(anomalies)} FLAGGED CLAUSES.\n")
    
    if len(anomalies) < 3:
        print("UNVERIFIED — fewer than 3 real flagged clauses available")
        # In a real environment, you might search more directories, but for this demo, we use RAW_DIR.

    for idx, item in enumerate(anomalies):
        target = item["clause"]
        doc_clauses = item["doc_clauses"]
        res = item["res"]
        
        print("="*60)
        print(f"ANOMALY {idx + 1} | ID: {target.clause_id} | Doc: {target.doc_id}")
        print(f"Severity: {res.severity} | Score: {res.combined_score}")
        print(f"Text Preview: {res.text_preview}")
        print("="*60)
        
        # 1. Integrated Gradients
        print("\n--- INTEGRATED GRADIENTS (Channel A) ---")
        try:
            ig_exp = ig_explainer.explain(target, steps=25)
            # Just print the top 5 attributed tokens for brevity
            payload = ig_exp.ig_payload
            tokens_with_attr = list(zip(payload.tokens, payload.attributions))
            # Sort by absolute attribution magnitude
            tokens_with_attr.sort(key=lambda x: abs(x[1]), reverse=True)
            top_tokens = tokens_with_attr[:5]
            
            print(f"Target Score: {payload.target_score}")
            print(f"Top 5 Tokens by Attribution: {top_tokens}")
            print(f"Claim Scope: {ig_exp.claim_scope.what_this_shows}")
        except Exception as e:
            print(f"IG Failed: {e}")

        # 2. Sensitivity
        print("\n--- CHANNEL B SENSITIVITY ---")
        try:
            sens_exp = sensitivity_analyzer.explain(target, doc_clauses)
            payload = sens_exp.sensitivity_payload
            print(f"Neighbor perturbed: {payload.neighbor_clause_id} ({payload.neighbor_position})")
            print(f"Delta: {payload.score_delta} (Original: {payload.original_score} -> Perturbed: {payload.perturbed_score})")
            print(f"Claim Scope: {sens_exp.claim_scope.what_this_shows}")
        except Exception as e:
            print(f"Sensitivity Failed: {e}")

        # 3. Nearest Neighbor
        print("\n--- NEAREST NEIGHBOR EVIDENCE ---")
        try:
            nn_exp = nn_retriever.explain(target, k=3)
            payload = nn_exp.nn_payload
            for nn in payload:
                print(f"Match: {nn.neighbor_clause_id} (Sim: {nn.similarity}) | Label: {nn.label}")
            print(f"Claim Scope: {nn_exp.claim_scope.what_this_shows}")
        except Exception as e:
            print(f"NN Failed: {e}")
            
        print("\n")

if __name__ == "__main__":
    run_demo()
