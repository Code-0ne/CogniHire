import numpy as np
import pandas as pd
import time
from sentence_transformers import CrossEncoder
from .loader import load_candidates
from .text_builder import build_rich_txt
from .sieve_engine import sieve_1, sieve_2
from .res_gen import generate_reasoning
from .config import CROSS_ENCODER_MODEL, TARGET_JD
from src.trajectory_engine import calculate_trajectory_scores

def rank_candidates(scored_candidates, candidates, jd_text, cross_model):

    pairs = []
    candidate_ids = []
    indices = []
    sieve2_scores = []
    
    for item in scored_candidates:
        txt = build_rich_txt(candidates[item["index"]])
        pairs.append([jd_text, txt])
        candidate_ids.append(item["candidate_id"])
        indices.append(item["index"])
        sieve2_scores.append(item["sieve2_score"])

    cross_scores = cross_model.predict(pairs, batch_size=32)

    results = []
    for i in range(len(cross_scores)):
        ce_raw = float(cross_scores[i])
        ce_score = 1 / (1 + np.exp(-ce_raw)) 
        
        s2_score = sieve2_scores[i]
        s2_norm = s2_score / 10.0 if s2_score > 1.0 else s2_score

        s2_item = scored_candidates[i]
        traj = s2_item.get("trajectory")
        if traj is None:
            traj = calculate_trajectory_scores(candidates[indices[i]])
        
        traj_val = (min(traj["production_ml_years"], 5) * 1 + 
                   min(traj["ranking_years"], 5) * 2 + 
                   min(traj["search_rec_years"], 5) * 1.5 +
                   (traj["vector_db_deployments"] * 0.5) + 
                   (traj["eval_framework_score"] * 0.3) + 
                   (traj["open_source_score"] * 0.5))
        traj_score = min(traj_val / 20.0, 1.0) 
        
        final_score = (0.60 * ce_score) + (0.25 * s2_norm) + (0.15 * traj_score)

        results.append({"candidate_id": candidate_ids[i], 
                        "index": indices[i], 
                        "score": final_score,
                        # Preserve metadata from Sieve 2
                        "required_skill_hits": s2_item.get("required_skill_hits", []),
                        "preferred_skill_hits": s2_item.get("preferred_skill_hits", []),
                        "system_hits": s2_item.get("system_hits", []),
                        "trajectory": s2_item.get("trajectory", {}),
                        "behavior_multiplier": s2_item.get("behavior_multiplier", 1.0),
                        "red_flags": s2_item.get("red_flags", 0)
                    })

    results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    return results[:100]

def main(output_file="team_PixelPioneers.csv"):
    start_time = time.time()
    candidates = load_candidates()
    if not candidates: return

    try:
        distances, top_indices = sieve_1(candidates)
    except FileNotFoundError:
        print("⚠️ JD embedding artifact not found. This script requires precomputation first.")
        return
    top_600 = sieve_2(distances, top_indices, candidates)

    
    print("🎯 Sieve 3: Precision Reranking...")
    cross_model = CrossEncoder(CROSS_ENCODER_MODEL)
    jd_text = TARGET_JD
    
    
    results_100 = rank_candidates(top_600, candidates, jd_text, cross_model)

    candidate_map = {c["candidate_id"]: c for c in candidates}
    submission_data = []
    for rank, res in enumerate(results_100, 1):
        cand_obj = candidate_map.get(res["candidate_id"]).copy()

        cand_obj["required_skill_hits"] = res.get("required_skill_hits", [])

        cand_obj["preferred_skill_hits"] = res.get("preferred_skill_hits", [])

        reasoning = generate_reasoning(cand_obj,rank,res["score"],jd_text)

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
