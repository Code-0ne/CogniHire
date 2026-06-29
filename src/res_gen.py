from src.config import REQUIRED_DOMAIN_KEYWORDS

def generate_reasoning(candidate, rank, final_score):
    if not candidate: return "Profile data missing."
    
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    
    total_months = sum([j.get("duration_months", 0) for j in career])
    yoe = round(total_months / 12, 1)
    top_title = career[0].get("title", "Engineer") if career else "Engineer"
    

    skills_list = candidate.get("skills", [])
    ai_skill_count = 0
    for s in skills_list:
        skill_name = s.get("name", "").lower()
        if any(kw in skill_name for kw in REQUIRED_DOMAIN_KEYWORDS):
            ai_skill_count += 1

    production_status = "no prod evidence"
    for job in career:
        desc = job.get("description", "").lower()
        if any(word in desc for word in ["deployed", "shipped", "scaled", "production"]):
            production_status = f"prod exp @ {job.get('company', 'ProductCo')}"
            break


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

    reasoning = f"{top_title} with {yoe} yrs; {ai_skill_count} AI core skills; {production_status}; {signal_text}{trade_off}."
    
    return reasoning
