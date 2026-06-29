import numpy as np
import faiss
from src.config import *
from src.jd_parser import get_jd_cont

def sieve_1(candidates=None, jd_vec=None):

    print("🔍 Sieve 1: Running Semantic Recall...")
    if jd_vec is not None:
        vector = jd_vec.astype('float32')
    else:
        vector = np.load(JD_EMBEDDING_PATH).astype('float32')
        
    index = faiss.read_index(FAISS_INDEX_PATH)
    

    D, I = index.search(vector, TOP_K_RECALL)
    return D[0].tolist(), I[0].tolist()

def sieve_2(distances, indices, candidates, jd_text=None):

    print("🧠 Sieve 2: Applying Intelligence Filters & Trap Detection...")
    scored_candidates = []


    jd = get_jd_cont(jd_text)

    for dist, idx in zip(distances, indices):
        cand = candidates[idx]
        
       
        base_score = 1.0 / (1.0 + dist)
        
        red_flags = 0
        multiplier = 1.0

       
        career = cand.get("career_history", [])
      
        total_months = sum([j.get("duration_months", 0) for j in career])
        yoe = total_months / 12
        

        companies = [j.get("company", "").lower() for j in career]
        if companies and all(any(c in comp for c in CONSULTING_FIRMS) for comp in companies):
            continue 

     
        rich_text = " ".join([j.get("description", "") for j in career]).lower()
        summary = cand.get("profile", {}).get("summary", "").lower()
        full_profile_text = rich_text + " " + summary
        if not any(word in full_profile_text for word in REQUIRED_DOMAIN_KEYWORDS):
            continue 

        # Direct Production Experience Scoring
        # Reward candidates who mention scaling, monitoring, indexing, etc.
        prod_keywords = PRODUCTION_KEYWORDS.union({"monitoring", "indexing", "observability", "kubernetes", "docker", "terraform"})
        prod_hits = [word for word in prod_keywords if word in full_profile_text]
        if len(prod_hits) >= 3:
            multiplier += SIGNAL_MODIFIERS["production_exp_bonus"]

        if len(career) > 1:
            avg_tenure = yoe / len(career)
            if avg_tenure < MAX_AVG_TENURE_FOR_STABILITY:
                red_flags += 1
            
            # Explicit Job Hopping Detection: Flag repeated short stints (< 18 months)
            short_stints = [j for j in career if j.get("duration_months", 0) < 18]
            if len(short_stints) >= 3:
                red_flags += 1 # Heavy penalty for habitual job hopping

        # --- Redrob Signal Integration ---
        sig = cand.get("redrob_signals", {})
        
        # 1. Profile Completeness (0-100)
        completeness = sig.get("profile_completeness_score", 0)
        if completeness < 40: red_flags += 1
        elif completeness > 80: multiplier += 0.05

        # 4. Open to Work
        if sig.get("open_to_work_flag"): 
            multiplier += SIGNAL_MODIFIERS["open_to_work_bonus"]

        # 7. Recruiter Response Rate (0.0-1.0)
        resp_rate = sig.get("recruiter_response_rate", 1.0)
        if resp_rate < 0.2: 
            multiplier += SIGNAL_MODIFIERS["low_response_penalty"]
        elif resp_rate > 0.8:
            multiplier += SIGNAL_MODIFIERS["high_response_bonus"]

        # 12. Notice Period (0-180 days)
        notice = sig.get("notice_period_days", 30)
        if notice > 60: 
            multiplier += SIGNAL_MODIFIERS["long_notice_penalty"]
        elif notice < 30: 
            multiplier += SIGNAL_MODIFIERS["fast_notice_bonus"]

        # 16. GitHub Activity Score (-1 to 100)
        gh_score = sig.get("github_activity_score", -1)
        if yoe > MIN_YEARS_FOR_EXTERNAL_VALIDATION:
            if gh_score == -1 and "paper" not in rich_text:
                red_flags += 1
        if gh_score > 70:
            multiplier += SIGNAL_MODIFIERS["github_active_bonus"]

        # 19. Interview Completion Rate (0.0-1.0)
        if sig.get("interview_completion_rate", 1.0) > 0.9:
            multiplier += SIGNAL_MODIFIERS["high_completion_bonus"]

        # 21 & 22. Verified Email/Phone
        if sig.get("verified_email") and sig.get("verified_phone"):
            multiplier += SIGNAL_MODIFIERS["verified_bonus"]

        # 17 & 18. Recruiter Interest (Search/Saved)
        if sig.get("saved_by_recruiters_30d", 0) > 5:
            multiplier += SIGNAL_MODIFIERS["high_demand_bonus"]

        # 3. Last Active Date (Recency check)
        # Simple check: if they haven't been active, apply inactive penalty
        # (Assuming a date string format, we just check if it exists for now)
        if not sig.get("last_active_date"):
            multiplier += SIGNAL_MODIFIERS["inactive_penalty"]
        

   
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
