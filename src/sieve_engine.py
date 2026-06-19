import numpy as np
import faiss
from datetime import datetime
from .config import *
from .jd_parser import get_jd_cont

def sieve_1(candidates):

    print("🔍 Sieve 1: Running Semantic Recall...")
    jd_vec = np.load(JD_EMBEDDING_PATH).astype('float32')
    index = faiss.read_index(FAISS_INDEX_PATH)
    
    D, I = index.search(jd_vec, TOP_K_RECALL)
    return I[0].tolist()

def sieve_2(candidate_indices, candidates):

    print("🧠 Sieve 2: Applying Intelligence Filters & Trap Detection...")
    jd = get_jd_cont()
    scored_candidates = []

    for idx in candidate_indices:
        cand = candidates[idx]
        
        base_score = 1.0 / (1.0 + idx)
        
        red_flags = 0
        multiplier = 1.0

        career = cand.get("career_history", [])
        companies = [j.get("company", "").lower() for j in career]
        if companies and all(any(c in comp for c in CONSULTING_FIRMS) for comp in companies):
            continue 

        if len(career) > 1:
            total_years = sum([(j.get("duration_months", 0)/12) for j in career])
            avg_tenure = total_years / len(career)
            if avg_tenure < MAX_AVG_TENURE_FOR_STABILITY:
                red_flags += 1

        rich_text = " ".join([j.get("description", "") for j in career]).lower()
        if any(w in rich_text for w in WRONG_DOMAIN_KEYWORDS) and not any(w in rich_text for w in REQUIRED_DOMAIN_KEYWORDS):
            red_flags += 1

        yoe = sum([j.get("duration_months", 0)/12 for j in career])
        if yoe > MIN_YEARS_FOR_EXTERNAL_VALIDATION:
            sig = cand.get("redrob_signals", {})
            if sig.get("github_activity_score", -1) == -1 and "paper" not in rich_text:
                red_flags += 1

        sig = cand.get("redrob_signals", {})
        if sig.get("open_to_work_flag"): multiplier += SIGNAL_MODIFIERS["open_to_work_bonus"]
        if sig.get("recruiter_response_rate", 1.0) < 0.2: multiplier += SIGNAL_MODIFIERS["low_response_penalty"]
        if sig.get("notice_period_days", 30) > 60: multiplier += SIGNAL_MODIFIERS["long_notice_penalty"]
        if sig.get("notice_period_days", 30) < 30: multiplier += SIGNAL_MODIFIERS["fast_notice_bonus"]

        loc = cand.get("profile", {}).get("location", "").lower()
        loc_multiplier = DEFAULT_LOCATION_MULTIPLIER
        for city, bonus in LOCATION_BONUSES.items():
            if city in loc:
                loc_multiplier = bonus
                break
        multiplier *= loc_multiplier

        final_multiplier = multiplier * (RED_FLAG_PENALTY ** red_flags)
        
        scored_candidates.append({
            "index": idx,
            "candidate_id": cand["candidate_id"],
            "sieve2_score": base_score * final_multiplier,
            "red_flags": red_flags
        })

    scored_candidates.sort(key=lambda x: x["sieve2_score"], reverse=True)
    return scored_candidates[:600]
