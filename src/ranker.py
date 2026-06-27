import numpy as np
import pandas as pd
import time
from sentence_transformers import CrossEncoder
from .loader import load_candidates
from .text_builder import build_rich_txt
from .sieve_engine import sieve_1, sieve_2
from .res_gen import generate_reasoning
from .config import CROSS_ENCODER_MODEL, TARGET_JD

def main(output_file="team_PixelPioneers.csv"):
    start_time = time.time()
    candidates = load_candidates()
    if not candidates: return

    
    distances, top_indices = sieve_1(candidates)
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
