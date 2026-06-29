import numpy as np
import pandas as pd
import time
from sentence_transformers import CrossEncoder
from .loader import load_candidates
from .text_builder import build_rich_txt
from .sieve_engine import sieve_1, sieve_2
from .res_gen import generate_reasoning
from .config import CROSS_ENCODER_MODEL, TARGET_JD

def rank_candidates(scored_candidates, candidates, jd_text, cross_model):
    """
    Precision Reranking logic (Sieve 3) extracted from the main ranker.
    
    Args:
        scored_candidates: Output from sieve_2 (list of dicts with 'index' and 'candidate_id')
        candidates: Full candidate list
        jd_text: Job Description text
        cross_model: The CrossEncoder model instance
    """
    pairs = []
    candidate_ids = []
    indices = []
    
    # Rerank the candidates passed from sieve_2
    for item in scored_candidates:
        txt = build_rich_txt(candidates[item["index"]])
        pairs.append([jd_text, txt])
        candidate_ids.append(item["candidate_id"])
        indices.append(item["index"])

    cross_scores = cross_model.predict(pairs, batch_size=32)

    results = []
    for i in range(len(cross_scores)):
        results.append({"candidate_id": candidate_ids[i], "index": indices[i], "score": float(cross_scores[i])})

    results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    return results[:100]

def main(output_file="team_PixelPioneers.csv"):
    start_time = time.time()
    candidates = load_candidates()
    if not candidates: return

    
    # The pipeline handles embedding generation, but for standalone ranker:
    # We use a dummy or precomputed JD vector. 
    # To fix the crash, we can try to load it or provide a fallback.
    try:
        distances, top_indices = sieve_1(candidates)
    except FileNotFoundError:
        print("⚠️ JD embedding artifact not found. This script requires precomputation first.")
        return
    top_600 = sieve_2(distances, top_indices, candidates)

    
    print("🎯 Sieve 3: Precision Reranking...")
    cross_model = CrossEncoder(CROSS_ENCODER_MODEL)
    jd_text = TARGET_JD
    
    pairs = []
    candidate_ids = []
    indices = []
    for item in top_600:
        pairs.append([jd_text, build_rich_txt(candidates[item["index"]])])
        candidate_ids.append(item["candidate_id"])
        indices.append(item["index"])

    cross_scores = cross_model.predict(pairs)

   
    results = []
    for i in range(len(cross_scores)):
        results.append({"candidate_id": candidate_ids[i], "index": indices[i], "score": float(cross_scores[i])})

    results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    final_100 = results[:100]

   
    candidate_map = {c["candidate_id"]: c for c in candidates}
    submission_data = []
    for rank, res in enumerate(final_100, 1):
        cand_obj = candidate_map.get(res["candidate_id"])
        reasoning = generate_reasoning(cand_obj, rank, res["score"])
        submission_data.append({
            "candidate_id": res["candidate_id"],
            "rank": rank,
            "score": res["score"],
            "reasoning": reasoning
        })

    pd.DataFrame(submission_data).to_csv(output_file, index=False)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Final submission saved to {output_file}")
    print(f"⏱️ Total execution time: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
