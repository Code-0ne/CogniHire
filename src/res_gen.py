from src.config import REQUIRED_DOMAIN_KEYWORDS

def generate_reasoning(candidate, rank, final_score):
    if not candidate: return "Profile data missing."
    
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    
    from src.trajectory_engine import calculate_trajectory_scores
    traj = calculate_trajectory_scores(candidate)
    
    total_months = sum([j.get("duration_months", 0) for j in career])
    yoe = round(total_months / 12, 1)
    top_title = career[0].get("title", "Engineer") if career else "Engineer"
    

    # Calculate a more discriminative "Technical Strength" score instead of raw AI skill count
    tech_score = (traj["production_ml_years"] * 2 + 
                  traj["ranking_years"] * 3 + 
                  traj["search_rec_years"] * 2 + 
                  traj["vector_db_deployments"] * 1)
    strength_label = f"Tech Score: {round(tech_score, 1)}"

    production_status = "no prod evidence"
    for job in career:
        desc = job.get("description", "").lower()
        if any(word in desc for word in ["deployed", "shipped", "scaled", "production"]):
            production_status = f"prod exp @ {job.get('company', 'ProductCo')}"
            break

    # Build Detailed Trajectory Summary for Reasoning
    traj_details = []
    if traj["production_ml_years"] > 0: traj_details.append(f"{traj['production_ml_years']}y Prod ML")
    if traj["ranking_years"] > 0: traj_details.append(f"{traj['ranking_years']}y Ranking")
    if traj["search_rec_years"] > 0: traj_details.append(f"{traj['search_rec_years']}y Search/Rec")
    if traj["vector_db_deployments"] > 0: traj_details.append(f"{traj['vector_db_deployments']} VectorDBs")
    if traj["eval_framework_score"] > 0: traj_details.append(f"Eval Frameworks")
    
    traj_text = " | ".join(traj_details) if traj_details else "general ML exp"

    resp_rate = signals.get("recruiter_response_rate", 0.0)
    notice = signals.get("notice_period_days", 30)
    
    if resp_rate < 0.2:
        signal_text = f"low resp rate {resp_rate:.2f}"
    elif notice > 60:
        signal_text = f"long notice {notice}d"
    elif signals.get("open_to_work_flag"):
        signal_text = "open to work"
    else:
        signal_text = f"resp rate {resp_rate:.2f}"


    trade_off = ""
    if rank > 50:
        if len(career) > 1 and (yoe / len(career)) < 1.8:
            trade_off = "; unstable tenure"
        elif not any(word in (profile.get("summary", "").lower()) for word in ["ndcg", "mrr", "map"]):
            trade_off = "; missing eval metrics"

    reasoning = f"{top_title} with {yoe} yrs; {strength_label}; {traj_text}; {production_status}; {signal_text}{trade_off}."
    
    return reasoning
